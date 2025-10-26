from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from langchain_community.callbacks import get_openai_callback
from typing import Optional, Literal
from langchain_community.document_loaders.parsers import LLMImageBlobParser
from langchain_openai import ChatOpenAI
from fastapi import UploadFile
from pydantic import BaseModel, Field
from app.core.config import settings
from llama_cloud_services import LlamaExtract
from app.core.config import settings
from app.prompts import post_process_text_prompt
from app.core.logging import get_logger
import tempfile
import os

logger = get_logger(__name__)


class KnowledgeDocument(BaseModel):
    title: str
    content: str


class DocumentService:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def extract_pdf(
        self,
        files: list[UploadFile],
        mode: Literal["single", "page"] = "single",
        extract_images: Optional[bool] = False,
    ) -> str:
        knowledge_documents: list[KnowledgeDocument] = []
        for file in files:
            contents = await file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(contents)
                temp_path = temp_file.name

            loader = PyMuPDF4LLMLoader(
                temp_path,
                mode=mode,
                pages_delimiter="\n\f",
                extract_images=extract_images,
                images_parser=LLMImageBlobParser(model=self.llm),
            )
            docs = loader.load()

            for doc in docs:
                formatted = await self._post_process_text_with_llm(doc.page_content)
                knowledge_documents.append(formatted)

            os.unlink(temp_path)

        return "\n".join(
            [f"{doc.title}\n\n{doc.content}" for doc in knowledge_documents]
        )

    async def _post_process_text_with_llm(self, text: str) -> KnowledgeDocument:
        chain = post_process_text_prompt | self.llm.with_structured_output(
            KnowledgeDocument
        )

        with get_openai_callback() as cb:
            data = chain.invoke({"text": text})
            logger.info(
                f"Chain metadata: total tokens:{cb.total_tokens} | total cost: ${cb.total_cost}"
            )
            return data

    async def extract_from_llama(self, files: list[UploadFile]) -> list[dict]:
        combined_text: list[dict] = []
        for file in files:
            contents = await file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(contents)
                temp_path = temp_file.name

            class KnowledgeDocument(BaseModel):
                question: str = Field(description="Question of the answer")
                answer: str = Field(description="Answer to the question")

            extractor = LlamaExtract(api_key=settings.llama_api_key)
            agents = extractor.list_agents()
            knowledge_base_extractor = [
                agent for agent in agents if agent.name == "knowledge-base-extractor"
            ][0]
            result = knowledge_base_extractor.extract(temp_path)
            print(result.data)
            combined_text.append(result.data)
        return combined_text
