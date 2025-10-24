import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.init_db import close_databases, init_databases


async def init_db():
    """Initialize the database."""
    print("Initializing databases...")
    await init_databases()
    print("Database initialization completed!")
    await close_databases()


if __name__ == "__main__":
    asyncio.run(init_db())
