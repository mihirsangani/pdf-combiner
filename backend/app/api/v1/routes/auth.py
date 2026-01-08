"""
Authentication routes: login, register, refresh token
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.base import get_db
from app.schemas.schemas import (
    UserCreate, UserLogin, UserResponse, 
    Token, RefreshTokenRequest, SuccessResponse
)
from app.services.auth_service import AuthService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters with digit and uppercase
    - **username**: Optional username
    - **full_name**: Optional full name
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.register_user(user_data)
        logger.info("User registered successfully", user_id=user.id, email=user.email)
        return user
    except ValueError as e:
        logger.warning("Registration failed", error=str(e), email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password
    
    Returns access token and refresh token
    """
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(
        credentials.email,
        credentials.password
    )
    
    if not user:
        logger.warning("Login failed - invalid credentials", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning("Login failed - inactive user", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    tokens = await auth_service.create_tokens(user.id)
    await auth_service.update_last_login(user.id)
    
    logger.info("User logged in successfully", user_id=user.id, email=user.email)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    auth_service = AuthService(db)
    
    try:
        tokens = await auth_service.refresh_tokens(request.refresh_token)
        logger.info("Token refreshed successfully")
        return tokens
    except ValueError as e:
        logger.warning("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user
    """
    auth_service = AuthService(db)
    
    user = await auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current user (token invalidation handled client-side)
    """
    logger.info("User logged out")
    return SuccessResponse(
        success=True,
        message="Logged out successfully"
    )


@router.post("/guest-token", response_model=dict)
async def create_guest_token():
    """
    Create a guest token for anonymous users
    """
    auth_service = AuthService(None)
    guest_token = auth_service.create_guest_token()
    
    logger.info("Guest token created")
    return {
        "guest_token": guest_token,
        "expires_in": 86400  # 24 hours
    }
