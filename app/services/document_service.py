from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from typing import Optional, Literal
from langchain_community.document_loaders.parsers import LLMImageBlobParser
from langchain_openai import ChatOpenAI
from fastapi import UploadFile
from app.core.config import settings
import tempfile
import os


class DocumentService:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    async def extract_pdf(
        self,
        files: list[UploadFile],
        mode: Literal["single", "multi"] = "single",
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
        return combined_text.replace("\f", "\n")
