from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from typing import List
from langchain_chroma import Chroma


class VectorService:
    def __init__(self, embeddings: OpenAIEmbeddings | GoogleGenerativeAIEmbeddings):
        self.embeddings = embeddings
        self.vector_store = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory="vector_store",
        )

    async def add_documents(self, documents: List[Document]) -> List[Document]:
        self.vector_store.add_documents(documents)
        return documents

    async def query_documents(self, query: str) -> List[Document]:
        return self.vector_store.similarity_search(query, k=2)

    async def delete_documents(self, documents: List[Document]) -> List[Document]:
        self.vector_store.delete_documents(documents)
        return documents

    async def delete_all_documents(self) -> List[Document]:
        self.vector_store.delete_all_documents()
        return []
