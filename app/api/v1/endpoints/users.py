from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_dependencies import get_current_superuser, get_current_user
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=list[User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser),
):
    """Get list of users (admin only)."""
    user_service = UserService()
    users = await user_service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get user by ID."""
    user_service = UserService()
    return await user_service.get_user(db, user_id)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update user."""
    # Users can only update their own profile unless they're superuser
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user_service = UserService()
    return await user_service.update_user(db, user_id, user_in)


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser),
):
    """Delete user (admin only)."""
    user_service = UserService()
    await user_service.delete_user(db, user_id)
    return {"message": "User deleted successfully"}


@router.patch("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser),
):
    """Activate user (admin only)."""
    user_service = UserService()
    user = await user_service.activate_user(db, user_id)
    return {"message": f"User {user.username} activated successfully"}


@router.patch("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser),
):
    """Deactivate user (admin only)."""
    user_service = UserService()
    user = await user_service.deactivate_user(db, user_id)
    return {"message": f"User {user.username} deactivated successfully"}
