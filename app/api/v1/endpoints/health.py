from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.db.mongodb import get_mongo_database
from app.db.session import get_db
from app.schemas.response import HealthCheckResponse

router = APIRouter()


async def get_db_optional() -> AsyncSession | None:
    """Get database session if available, return None if connection fails."""
    try:
        async for session in get_db():
            return session
    except Exception:
        return None


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: AsyncSession | None = Depends(get_db_optional)):
    """Health check endpoint."""
    database_status = {}

    # Check PostgreSQL
    if db is not None:
        try:
            await db.execute(text("SELECT 1"))
            database_status["postgresql"] = "healthy"
        except Exception as e:
            database_status["postgresql"] = f"unhealthy: {str(e)}"
    else:
        database_status["postgresql"] = "not connected"

    # Check MongoDB
    try:
        mongo_db = get_mongo_database()
        await mongo_db.command("ping")
        database_status["mongodb"] = "healthy"
    except Exception as e:
        database_status["mongodb"] = f"unhealthy: {str(e)}"

    # Application is healthy if it can respond, regardless of database status
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
        environment=settings.environment,
        database_status=database_status,
    )


@router.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"message": "pong", "timestamp": datetime.now(timezone.utc)}
