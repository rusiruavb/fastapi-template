from typing import Optional, Any
from langchain_chroma import Chroma
from app.clients.base_client import BaseClient
from app.core.config import settings


class ChromaClient(BaseClient[Chroma]):
    """Chroma vector store client."""

    def __init__(
        self,
        embeddings: Any,
        collection_name: Optional[str] = "documents",
        persist_directory: Optional[str] = "vector_store",
        **kwargs,
    ):
        super().__init__()
        self.client: Chroma = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            chroma_cloud_api_key=settings.chroma_api_key,
            tenant=settings.chroma_tenant,
            database=settings.chroma_database,
            **kwargs,
        )

    def get_client(self) -> Chroma:
        return self.client
