from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MongoDocument(BaseModel):
    """Base MongoDB document schema."""

    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserDocument(MongoDocument):
    """User document for MongoDB."""

    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str
    full_name: str | None = Field(None, max_length=100)
    is_active: bool = True
    is_superuser: bool = False
    bio: str | None = None
    avatar_url: str | None = None


class UserDocumentCreate(BaseModel):
    """Schema for creating a user document."""

    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str
    full_name: str | None = Field(None, max_length=100)
    bio: str | None = None
    avatar_url: str | None = None
    is_active: bool = True
    is_superuser: bool = False


class UserDocumentUpdate(BaseModel):
    """Schema for updating a user document."""

    email: str | None = Field(None, max_length=255)
    username: str | None = Field(None, min_length=3, max_length=50)
    full_name: str | None = Field(None, max_length=100)
    bio: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None
