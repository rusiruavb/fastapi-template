import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.security import get_password_hash
from app.db.init_db import init_databases
from app.db.session import AsyncSessionLocal
from app.models.user import User


async def create_superuser():
    """Create a superuser account."""
    await init_databases()

    async with AsyncSessionLocal() as db:
        # Check if superuser already exists
        existing_user = await db.execute(
            "SELECT id FROM users WHERE is_superuser = true LIMIT 1"
        )
        if existing_user.scalar_one_or_none():
            print("Superuser already exists!")
            return

        # Create superuser
        superuser = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrator",
            is_active=True,
            is_superuser=True,
        )

        db.add(superuser)
        await db.commit()
        await db.refresh(superuser)

        print(f"Superuser created successfully!")
        print(f"Email: {superuser.email}")
        print(f"Username: {superuser.username}")
        print(f"Password: admin123")


if __name__ == "__main__":
    asyncio.run(create_superuser())
