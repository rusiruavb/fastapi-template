from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.mongodb import get_mongo_database
from app.db.session import get_db

logger = get_logger(__name__)


async def init_databases() -> None:
    """Initialize both PostgreSQL and MongoDB."""
    try:
        # Initialize PostgreSQL
        from app.db.session import init_db

        await init_db()
        logger.info("PostgreSQL database initialized")

        # Initialize MongoDB
        from app.db.mongodb import connect_to_mongo

        await connect_to_mongo()
        logger.info("MongoDB database initialized")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_databases() -> None:
    """Close database connections."""
    try:
        from app.db.mongodb import close_mongo_connection

        await close_mongo_connection()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
