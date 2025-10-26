from .auth import router as auth_router
from .health import router as health_router
from .users import router as users_router
from .documents import router as documents_router

__all__ = ["auth_router", "health_router", "users_router", "documents_router"]
