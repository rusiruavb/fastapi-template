from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str | None = Field(None, max_length=100)
    bio: str | None = None
    avatar_url: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    full_name: str | None = Field(None, max_length=100)
    bio: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None


class UserInDB(UserBase):
    """Schema for user in database."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class User(UserInDB):
    """Schema for user response."""

    pass


class UserProfile(BaseModel):
    """Schema for user profile (public info)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    full_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    created_at: datetime


class UserList(BaseModel):
    """Schema for user list response."""

    users: list[User]
    total: int
    page: int
    size: int
    pages: int
