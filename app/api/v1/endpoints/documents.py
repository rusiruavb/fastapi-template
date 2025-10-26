from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from typing import Annotated
from fastapi.responses import Response
from langchain_chroma import Chroma
from app.core.dependencies import (
    get_chroma_vector_client,
    get_chunk_service,
    get_document_service,
)
from app.services.chunk_service import ChunkService
from app.services.document_service import DocumentService
import json

router = APIRouter()


@router.post("/upload")
async def upload_documents(
    files: Annotated[
        list[UploadFile], File(description="Knowledge base document files")
    ],
    chunk_service: ChunkService = Depends(get_chunk_service),
    document_service: DocumentService = Depends(get_document_service),
    chroma: Chroma = Depends(get_chroma_vector_client),
):
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    text = await document_service.extract_pdf(files)
    chunks = await chunk_service.semantic_chunk(
        text, breakpoint_threshold_type="percentile", breakpoint_threshold_amount=90
    )

    chroma.add_documents(chunks)
    return Response(content=text, status_code=200)
