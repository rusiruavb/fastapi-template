import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.init_db import close_databases, init_databases
from app.middleware.error_handler import setup_exception_handlers
from app.middleware.logging import LoggingMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up FastAPI application")
    try:
        await init_databases()
        logger.info("Database connections initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        logger.info("Application will start without database connections")

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application")
    try:
        await close_databases()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.warning(f"Error closing database connections: {e}")


def create_app() -> FastAPI:
    """Create FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        description=("A FastAPI API for FastAPI AI"),
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add logging middleware
    app.add_middleware(LoggingMiddleware)

    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include API router
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to FastAPI AI API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    return app


# Create app instance
app = create_app()
