from fastapi import Depends, Query
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.clients import ClientFactory
from app.clients.constants import OPENAI_MODEL_OPTIONS, OPENAI_EMBEDDING_MODEL_OPTIONS
from typing import Optional

from app.services.chunk_service import ChunkService
from app.services.document_service import DocumentService


async def get_openai_embedding_client(
    model: Optional[OPENAI_EMBEDDING_MODEL_OPTIONS] = Query(
        default="text-embedding-3-large", description="OpenAI embedding model to use"
    ),
) -> OpenAIEmbeddings:
    return ClientFactory.get_openai_embedding_client(model=model)


async def get_openai_llm_client(
    model: Optional[OPENAI_MODEL_OPTIONS] = Query(
        default="gpt-4o-mini", description="OpenAI LLM model to use"
    ),
) -> ChatOpenAI:
    return ClientFactory.get_openai_llm_client(model=model)


async def get_chroma_vector_client(embeddings: OpenAIEmbeddings) -> Chroma:
    return ClientFactory.get_chroma_vector_client(embeddings=embeddings)


async def get_chunk_service(
    embeddings: OpenAIEmbeddings = Depends(get_openai_embedding_client),
    llm: ChatOpenAI = Depends(get_openai_llm_client),
) -> ChunkService:
    return ChunkService(embeddings=embeddings, llm=llm)


async def get_document_service(
    llm: ChatOpenAI = Depends(get_openai_llm_client),
) -> DocumentService:
    return DocumentService(llm=llm)
