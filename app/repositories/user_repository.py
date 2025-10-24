from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository for PostgreSQL."""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """Get user by email."""
        return await self.get_by_field(db, field_name="email", value=email)

    async def get_by_username(self, db: AsyncSession, *, username: str) -> User | None:
        """Get user by username."""
        return await self.get_by_field(db, field_name="username", value=username)

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        obj_data = obj_in.model_dump()
        obj_data["hashed_password"] = get_password_hash(obj_data.pop("password"))
        db_obj = User(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, db: AsyncSession, *, username: str, password: str
    ) -> User | None:
        """Authenticate user with username/email and password."""
        # Try to find user by username or email
        user = await self.get_by_username(db, username=username)
        if not user:
            user = await self.get_by_email(db, email=username)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """Check if user is superuser."""
        return user.is_superuser
