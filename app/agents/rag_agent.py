from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from typing import Annotated, List, Literal
from langchain_core.documents import Document
from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from langgraph.graph.message import BaseMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field
from IPython.display import Image, display
from langgraph.graph import MessagesState

GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
)

REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Formulate an improved question:"
)

GENERATE_PROMPT = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, just say that you don't know. "
    "Use three sentences maximum and keep the answer concise.\n"
    "Question: {question} \n"
    "Context: {context}"
)

MAX_REWRITES = 2

SYSTEM_TOOL_INSTRUCTION = (
    "You are part of a retrieval-augmented system. "
    "Before answering, you MUST call the `retrieve_documents` tool with the user's question "
    "to fetch context from the vector store. Do not answer without first retrieving."
)


class GradeDocuments(BaseModel):
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


class RAGAgentState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages]
    rewrites: int = 0


class RAGAgent:
    def __init__(self, vector_store_retriever: VectorStoreRetriever, llm: ChatOpenAI):
        self.vector_store_retriever = vector_store_retriever
        self.llm = llm
        self.graph = StateGraph(MessagesState)

    @tool(
        response_format="content_and_artifact",
        description="Retrieve documents from the vector store given a natural language query.",
    )
    def retrieve_documents(self, query: str) -> str:
        docs = self.vector_store_retriever.get_relevant_documents(query)
        print(docs)
        context = "\n\n".join(
            d.page_content for d in docs if getattr(d, "page_content", None)
        )
        return context

    def generate_query_or_respond(self, state: RAGAgentState) -> RAGAgentState:
        response = self.llm.bind_tools([self.retrieve_documents]).invoke(state.messages)
        print(response)
        return {"messages": [response]}

    def grade_documents(
        self, state: RAGAgentState
    ) -> Literal["generate_answer", "rewrite_question", "no_answer"]:
        question = state.messages[0].content
        context = state.messages[-1].content

        # If retrieval returned nothing, bail out or try limited rewrites
        if not str(context).strip():
            if state.rewrites >= MAX_REWRITES:
                return "no_answer"
            return "rewrite_question"

        prompt = GRADE_PROMPT.format(question=question, context=context)
        response = self.llm.with_structured_output(GradeDocuments).invoke(
            [{"role": "user", "content": prompt}]
        )
        score = response.binary_score

        if score == "yes":
            return "generate_answer"
        if state.rewrites >= MAX_REWRITES:
            return "no_answer"
        return "rewrite_question"

    def rewrite_question(self, state: RAGAgentState) -> RAGAgentState:
        messages = state.messages
        question = messages[0].content
        prompt = REWRITE_PROMPT.format(question=question)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {
            "messages": [{"role": "user", "content": response.content}],
            "rewrites": state.rewrites + 1,
        }

    def generate_answer(self, state: RAGAgentState) -> RAGAgentState:
        question = state.messages[0].content
        context = state.messages[-1].content
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response], "rewrites": state.rewrites}

    def no_answer(self, state: RAGAgentState) -> RAGAgentState:
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": "I couldn't find relevant context to answer this. Please try rephrasing or provide more details.",
                }
            ],
            "rewrites": state.rewrites,
        }

    def get_graph(
        self,
    ) -> CompiledStateGraph[RAGAgentState, None, RAGAgentState, RAGAgentState]:
        self.graph.add_node("generate_query_or_respond", self.generate_query_or_respond)
        self.graph.add_node("retrieve", ToolNode([self.retrieve_documents]))
        self.graph.add_node("rewrite_question", self.rewrite_question)
        self.graph.add_node("generate_answer", self.generate_answer)
        self.graph.add_node("no_answer", self.no_answer)

        self.graph.add_edge(START, "generate_query_or_respond")
        self.graph.add_edge("generate_query_or_respond", "retrieve")
        self.graph.add_conditional_edges(
            "retrieve",
            self.grade_documents,
        )
        self.graph.add_edge("generate_answer", END)
        self.graph.add_edge("no_answer", END)
        self.graph.add_edge("rewrite_question", "generate_query_or_respond")

        graph = self.graph.compile()

        with open("rag_graph.png", "wb") as f:
            f.write(graph.get_graph().draw_mermaid_png())

        return graph
