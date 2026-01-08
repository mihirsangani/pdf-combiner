"""
User management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.schemas import UserResponse, UserUpdate, UserDashboard
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.api.v1.routes.auth import security
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter()


async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Dependency to get current active user"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return user


@router.get("/dashboard", response_model=UserDashboard)
async def get_dashboard(
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user dashboard with statistics
    """
    user_service = UserService(db)
    dashboard = await user_service.get_user_dashboard(current_user.id)
    return dashboard


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get current user profile
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile
    """
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user.id, user_update)
    return updated_user


@router.delete("/account")
async def delete_account(
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete current user account
    """
    user_service = UserService(db)
    await user_service.delete_user(current_user.id)
    
    return {
        "success": True,
        "message": "Account deleted successfully"
    }
