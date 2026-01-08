"""
Authentication service - handles user authentication and token management
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from app.models.models import User
from app.schemas.schemas import UserCreate
from app.core.security import (
    verify_password, get_password_hash,
    create_token_pair, decode_token
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: Optional[AsyncSession]):
        self.db = db
    
    async def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email exists
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if username exists (if provided)
        if user_data.username:
            result = await self.db.execute(
                select(User).where(User.username == user_data.username)
            )
            existing_username = result.scalar_one_or_none()
            
            if existing_username:
                raise ValueError("Username already taken")
        
        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            is_active=True,
            is_verified=False
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate_user(
        self, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: Plain password
            
        Returns:
            User if authentication successful, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def create_tokens(self, user_id: int) -> dict:
        """
        Create access and refresh tokens for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with tokens
        """
        return create_token_pair(user_id)
    
    async def refresh_tokens(self, refresh_token: str) -> dict:
        """
        Create new tokens from refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token pair
            
        Raises:
            ValueError: If token is invalid
        """
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")
        
        return create_token_pair(int(user_id))
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current user from access token
        
        Args:
            token: Access token
            
        Returns:
            User if token is valid, None otherwise
        """
        payload = decode_token(token)
        
        if not payload or payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        result = await self.db.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        return user
    
    async def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.last_login = datetime.utcnow()
            await self.db.commit()
    
    def create_guest_token(self) -> str:
        """
        Create a guest token for anonymous users
        
        Returns:
            Guest token string
        """
        return f"guest_{secrets.token_urlsafe(32)}"
