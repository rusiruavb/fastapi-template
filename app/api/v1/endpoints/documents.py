from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from typing import Annotated
from fastapi.responses import Response
from app.core.dependencies import (
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
):
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    text = await document_service.extract_pdf(files)
    chunks = await chunk_service.semantic_chunk(text)
    return Response(content=json.dumps(chunks), media_type="application/json")
