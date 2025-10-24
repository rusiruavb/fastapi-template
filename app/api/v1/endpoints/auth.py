from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.token import LoginRequest, RefreshTokenRequest, Token
from app.schemas.user import User, UserCreate
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login endpoint."""
    auth_service = AuthService()
    return await auth_service.login(db, login_data)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    auth_service = AuthService()
    return await auth_service.refresh_token(refresh_data.refresh_token)


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post("/register", response_model=User)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    user_service = UserService()
    return await user_service.create_user(db, user_in)
