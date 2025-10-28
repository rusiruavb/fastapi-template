from fastapi import APIRouter, Depends
from langchain_openai import ChatOpenAI
from app.agents.rag_agent import RAGAgent
from app.core.dependencies import (
    get_openai_llm_client,
    get_vector_store_retriever,
)
from langchain_core.vectorstores import VectorStoreRetriever

router = APIRouter()


@router.post("/rag")
async def rag(
    query: str,
    retriever: VectorStoreRetriever = Depends(get_vector_store_retriever),
    llm: ChatOpenAI = Depends(get_openai_llm_client),
):
    rag_agent = RAGAgent(retriever, llm)
    graph = rag_agent.get_graph()
    result = graph.invoke({"messages": [{"role": "user", "content": query}]})

    return result.get("messages", [])[-1].content
