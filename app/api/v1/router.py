from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth_router,
    health_router,
    users_router,
    documents_router,
    rag_router,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(rag_router, prefix="/rag", tags=["rag"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
