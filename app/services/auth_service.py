from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import create_token_pair, verify_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.token import LoginRequest, Token
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate

logger = get_logger(__name__)


class AuthService:
    """Authentication service."""

    def __init__(self):
        self.user_repo = UserRepository()

    async def login(self, db: AsyncSession, login_data: LoginRequest) -> Token:
        """Authenticate user and return tokens."""
        user = await self.user_repo.authenticate(
            db, username=login_data.username, password=login_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not await self.user_repo.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        # Create token pair
        token_data = create_token_pair(str(user.id))

        logger.info(f"User {user.username} logged in successfully")
        return Token(**token_data)

    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token."""
        try:
            user_id = verify_token(refresh_token, token_type="refresh")
            # Create new token pair
            token_data = create_token_pair(user_id)
            return Token(**token_data)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(self, db: AsyncSession, token: str) -> User:
        """Get current user from access token."""
        try:
            user_id = verify_token(token, token_type="access")
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self.user_repo.get(db, id=user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not await self.user_repo.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        return user

    async def get_current_active_user(self, db: AsyncSession, token: str) -> User:
        """Get current active user."""
        return await self.get_current_user(db, token)

    async def get_current_superuser(self, db: AsyncSession, token: str) -> User:
        """Get current superuser."""
        user = await self.get_current_user(db, token)
        if not await self.user_repo.is_superuser(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
        return user
