from typing import Annotated, List
from pydantic import BaseModel, Field

import operator
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.graph.message import BaseMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from IPython.display import Image, display


# -------- Constants --------
NUM_QUERY_EXPANSIONS: int = 3
RETRIEVER_K: int = 12
MAX_CONTEXT_CHUNKS: int = 12

GRADE_PROMPT = None
REWRITE_PROMPT = None

GENERATE_PROMPT = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, just say that you don't know. "
    "Use three sentences maximum and keep the answer concise.\n"
    "Question: {question} \n"
    "Context: {context}"
)

MULTI_QUERY_PROMPT = (
    "Generate {n} diverse reformulations of the following question that could retrieve different relevant documents.\n"
    "Return each variation on a new line, concise but semantically distinct.\n\n"
    "Question: {question}"
)


class RAGAgentState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages]
    context_text: Annotated[str, operator.add] = ""


class RAGAgent:
    def __init__(self, vector_store_retriever: VectorStoreRetriever, llm: ChatOpenAI):
        self.vector_store_retriever = vector_store_retriever
        self.llm = llm
        self.graph = StateGraph[RAGAgentState, None, RAGAgentState, RAGAgentState](
            state_schema=RAGAgentState
        )

    @tool(
        response_format="content_and_artifact",
        description="Retrieve documents from the vector store",
    )
    def _retrieve_documents(self, query: str) -> List[Document]:
        return self.vector_store_retriever.invoke(input=query)

    # -------- Helpers to access state messages safely --------

    def _get_user_question(self, state: RAGAgentState) -> str:
        for m in state.messages:
            if getattr(m, "type", "") == "human":
                return str(m.content)
        return str(state.messages[0].content) if state.messages else ""

    def _get_retrieved_docs(self, state: RAGAgentState) -> List[Document]:
        for m in reversed(state.messages):
            if (
                getattr(m, "type", "") == "tool"
                and getattr(m, "name", "") == "_retrieve_documents"
            ):
                artifact = getattr(m, "artifact", None)
                if (
                    isinstance(artifact, list)
                    and artifact
                    and isinstance(artifact[0], Document)
                ):
                    return artifact  # List[Document]
                return []
        return []

    def _docs_to_context(self, docs: List[Document]) -> str:
        if not docs:
            return ""
        return "\n\n".join(
            [d.page_content for d in docs if getattr(d, "page_content", None)]
        )

    def _expand_queries(self, question: str, n: int) -> List[str]:
        try:
            prompt = MULTI_QUERY_PROMPT.format(question=question, n=n)
            resp = self.llm.invoke([{"role": "user", "content": prompt}])
            lines = [ln.strip(" -\t") for ln in resp.content.splitlines()]
            variations = [ln for ln in lines if ln]
            # Ensure uniqueness and cap to n
            unique: List[str] = []
            for v in variations:
                if v not in unique:
                    unique.append(v)
                if len(unique) >= n:
                    break
            return unique
        except Exception:
            return []

    def _dedupe_docs(self, docs: List[Document]) -> List[Document]:
        seen_keys = set()
        deduped: List[Document] = []
        for d in docs:
            meta = getattr(d, "metadata", {}) or {}
            key = (
                meta.get("id")
                or meta.get("source")
                or meta.get("doc_id")
                or d.page_content[:200]
            )
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped.append(d)
        return deduped[:MAX_CONTEXT_CHUNKS]

    # -------- Nodes --------

    def _retrieve(self, state: RAGAgentState) -> RAGAgentState:
        # Deterministically retrieve using the current user question
        question = self._get_user_question(state)

        # Try to tune retriever for higher recall (best-effort; attributes may not exist)
        try:
            if hasattr(self.vector_store_retriever, "search_kwargs"):
                self.vector_store_retriever.search_kwargs.update(
                    {
                        "k": RETRIEVER_K,
                        "fetch_k": max(RETRIEVER_K * 3, 20),
                        "lambda_mult": 0.5,  # for MMR if supported
                    }
                )
            if hasattr(self.vector_store_retriever, "search_type"):
                # switch to mmr if available
                setattr(self.vector_store_retriever, "search_type", "mmr")
            if hasattr(self.vector_store_retriever, "k"):
                setattr(self.vector_store_retriever, "k", RETRIEVER_K)
        except Exception:
            pass

        # Multi-query expansion
        variations = self._expand_queries(question, NUM_QUERY_EXPANSIONS)
        queries = [question] + [v for v in variations if v and v != question]

        all_docs: List[Document] = []
        for q in queries:
            try:
                batch = self.vector_store_retriever.invoke(input=q)
                if isinstance(batch, list):
                    all_docs.extend(batch)
            except Exception:
                continue

        if not all_docs:
            context = ""
        else:
            context = self._docs_to_context(self._dedupe_docs(all_docs))
        return {"context_text": context}

    # Removed grading/rewrite/give_up for simplified 2-node flow

    def _generate_answer(self, state: RAGAgentState) -> RAGAgentState:
        question = self._get_user_question(state)
        context = state.context_text or ""
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}

    def get_graph(
        self,
    ) -> CompiledStateGraph[RAGAgentState, None, RAGAgentState, RAGAgentState]:
        self.graph.add_node("retrieve", self._retrieve)
        self.graph.add_node("gen_answer", self._generate_answer)

        self.graph.add_edge(START, "retrieve")
        self.graph.add_edge("retrieve", "gen_answer")
        self.graph.add_edge("gen_answer", END)

        graph = self.graph.compile()
        # write the graph to a file
        with open("rag_graph.png", "wb") as f:
            f.write(graph.get_graph().draw_mermaid_png())
        return graph
