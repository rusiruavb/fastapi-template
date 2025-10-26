from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_experimental.text_splitter import BreakpointThresholdType
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
from typing import List
from app.utils.agentic_chunker import AgenticChunker, GetType


class ChunkService:
    def __init__(
        self,
        embeddings: OpenAIEmbeddings | GoogleGenerativeAIEmbeddings,
        llm: ChatOpenAI,
    ):
        self.embeddings = embeddings
        self.llm = llm

    async def semantic_chunk(
        self,
        text: str,
        breakpoint_threshold_type: BreakpointThresholdType = "interquartile",
        breakpoint_threshold_amount: int = 10,
    ) -> List[Document]:
        semantic_chunker = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type=breakpoint_threshold_type,
            breakpoint_threshold_amount=breakpoint_threshold_amount,
        )
        documents = semantic_chunker.create_documents([text])
        return documents

    async def agentic_chunk(self, text: str) -> List[Document]:
        agentic_chunker = AgenticChunker(llm=self.llm)
        propositions = agentic_chunker.get_propositions(text)
        agentic_chunker.add_propositions(propositions)
        chunks = agentic_chunker.get_chunks(get_type=GetType.LIST_OF_STRING)
        documents = [Document(page_content=chunk) for chunk in chunks]
        return documents

    async def markdown_header_chunk(self, text: str) -> List[Document]:
        markdown_header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "Title")], strip_headers=True
        )
        documents = markdown_header_splitter.split_text(text)
        return documents
