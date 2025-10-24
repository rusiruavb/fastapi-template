from typing import Literal
from langchain_openai import OpenAIEmbeddings
from app.clients.base_client import BaseClient
from app.clients.constants import OPENAI_EMBEDDING_MODEL_OPTIONS


class OpenAIEmbeddingClient(BaseClient[OpenAIEmbeddings]):
    """OpenAI embedding client."""

    def __init__(
        self,
        api_key: str,
        model: OPENAI_EMBEDDING_MODEL_OPTIONS = "text-embedding-3-large",
        **kwargs,
    ):
        super().__init__()
        self.client: OpenAIEmbeddings = OpenAIEmbeddings(
            api_key=api_key, model=model, **kwargs
        )

    def get_client(self) -> OpenAIEmbeddings:
        return self.client
