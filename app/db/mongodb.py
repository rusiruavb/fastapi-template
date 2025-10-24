from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


class MongoDB:
    """MongoDB connection manager."""

    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    """Create database connection."""
    mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
    mongodb.database = mongodb.client[settings.mongodb_database]


async def close_mongo_connection() -> None:
    """Close database connection."""
    if mongodb.client:
        mongodb.client.close()


def get_mongo_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance."""
    if mongodb.database is None:
        raise RuntimeError("MongoDB not initialized")
    return mongodb.database


def get_mongo_collection(collection_name: str):
    """Get MongoDB collection."""
    database = get_mongo_database()
    return database[collection_name]
