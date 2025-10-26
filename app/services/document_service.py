from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from typing import Optional, Literal
from langchain_community.document_loaders.parsers import LLMImageBlobParser
from langchain_openai import ChatOpenAI
from fastapi import UploadFile
from pydantic import BaseModel, Field
from app.core.config import settings
from llama_cloud_services import LlamaExtract
from app.core.config import settings
import tempfile
import os


class DocumentService:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def extract_pdf(
        self,
        files: list[UploadFile],
        mode: Literal["single", "page"] = "single",
        extract_images: Optional[bool] = False,
    ) -> str:
        """
        Extract text from PDF files using `PyMuPDF4LLMLoader`.

        Args:
            `files`: List of PDF files to extract text from.
            `mode`: Mode to use for extracting text.
            `extract_images`: Whether to extract images from the PDF files.
        """
        combined_text = ""
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
            combined_text += "".join([doc.page_content for doc in docs])
            os.unlink(temp_path)
        text = combined_text.replace("\f", "\n").replace("\n\n", "\n")
        return text

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
