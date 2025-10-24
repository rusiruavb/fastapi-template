from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserList, UserUpdate

logger = get_logger(__name__)


class UserService:
    """User service for business logic."""

    def __init__(self):
        self.user_repo = UserRepository()

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        print(user_in)
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        existing_user = await self.user_repo.get_by_username(
            db, username=user_in.username
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        user = await self.user_repo.create(db, obj_in=user_in)
        logger.info(f"User {user.username} created successfully")
        return user

    async def get_user(self, db: AsyncSession, user_id: UUID) -> User:
        """Get user by ID."""
        user = await self.user_repo.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def get_users(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Get list of users with pagination."""
        users = await self.user_repo.get_multi(db, skip=skip, limit=limit)
        return users

    async def update_user(
        self, db: AsyncSession, user_id: UUID, user_in: UserUpdate
    ) -> User:
        """Update user."""
        user = await self.get_user(db, user_id)

        # Check if email is being changed and if it's already taken
        if user_in.email and user_in.email != user.email:
            existing_user = await self.user_repo.get_by_email(db, email=user_in.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

        # Check if username is being changed and if it's already taken
        if user_in.username and user_in.username != user.username:
            existing_user = await self.user_repo.get_by_username(
                db, username=user_in.username
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

        updated_user = await self.user_repo.update(db, db_obj=user, obj_in=user_in)
        logger.info(f"User {updated_user.username} updated successfully")
        return updated_user

    async def delete_user(self, db: AsyncSession, user_id: UUID) -> User:
        """Delete user."""
        user = await self.get_user(db, user_id)
        deleted_user = await self.user_repo.remove(db, id=user_id)
        logger.info(f"User {user.username} deleted successfully")
        return deleted_user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Get user by email."""
        return await self.user_repo.get_by_email(db, email=email)

    async def get_user_by_username(
        self, db: AsyncSession, username: str
    ) -> User | None:
        """Get user by username."""
        return await self.user_repo.get_by_username(db, username=username)

    async def activate_user(self, db: AsyncSession, user_id: UUID) -> User:
        """Activate user."""
        user = await self.get_user(db, user_id)
        user.is_active = True
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User {user.username} activated")
        return user

    async def deactivate_user(self, db: AsyncSession, user_id: UUID) -> User:
        """Deactivate user."""
        user = await self.get_user(db, user_id)
        user.is_active = False
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User {user.username} deactivated")
        return user
