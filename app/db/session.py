from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from fastapi import HTTPException

from app.core.config import settings
from app.db.base import Base

# SQLAlchemy async engine - created lazily to handle connection failures
engine = None
AsyncSessionLocal = None


def get_engine():
    """Get or create the database engine."""
    global engine
    if engine is None:
        try:
            engine = create_async_engine(
                settings.postgres_url, echo=settings.debug, future=True
            )
        except Exception as e:
            raise Exception(f"Failed to create database engine: {e}")
    return engine


def get_session_factory():
    """Get or create the session factory."""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        try:
            AsyncSessionLocal = async_sessionmaker(
                get_engine(), class_=AsyncSession, expire_on_commit=False
            )
        except Exception as e:
            raise Exception(f"Failed to create session factory: {e}")
    return AsyncSessionLocal


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.close()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )


async def init_db() -> None:
    """Initialize database tables."""
    try:
        db_engine = get_engine()
        async with db_engine.begin() as conn:
            # Import all models here to ensure they are registered
            from app.models import user  # noqa

            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        raise Exception(f"Failed to initialize database: {e}")
