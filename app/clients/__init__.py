from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.clients.embeddings import OpenAIEmbeddingClient
from app.clients.llm import OpenAiLLMClient
from app.core.config import settings
from app.clients.vector import ChromaClient
from app.clients.constants import (
    OPENAI_MODEL_OPTIONS,
    OPENAI_EMBEDDING_MODEL_OPTIONS,
)


class ClientFactory:
    """Client factory for creating clients."""

    @staticmethod
    def get_openai_llm_client(
        model: Optional[OPENAI_MODEL_OPTIONS] = "gpt-4o-mini", **kwargs
    ) -> ChatOpenAI:
        try:
            if settings.openai_api_key is None:
                raise ValueError("OpenAI API key is not set")

            return OpenAiLLMClient(
                api_key=settings.openai_api_key, model=model, **kwargs
            ).get_client()
        except Exception as e:
            raise ValueError(f"Error creating OpenAI LLM client: {e}")

    @staticmethod
    def get_openai_embedding_client(
        model: Optional[OPENAI_EMBEDDING_MODEL_OPTIONS] = "text-embedding-3-large",
        **kwargs,
    ) -> OpenAIEmbeddings:
        try:
            if settings.openai_api_key is None:
                raise ValueError("OpenAI API key is not set")

            return OpenAIEmbeddingClient(
                api_key=settings.openai_api_key, model=model, **kwargs
            ).get_client()
        except Exception as e:
            raise ValueError(f"Error creating OpenAI embedding client: {e}")

    @staticmethod
    def get_chroma_vector_client(
        embeddings: OpenAIEmbeddings, **kwargs
    ) -> ChromaClient:
        try:
            if embeddings is None:
                raise ValueError("Embeddings are not set")

            return ChromaClient(embeddings=embeddings, **kwargs)
        except Exception as e:
            raise ValueError(f"Error creating Chroma vector client: {e}")
