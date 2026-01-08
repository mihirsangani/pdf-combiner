"""
File service - handles file operations
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from datetime import datetime

from app.models.models import File
from app.core.logging import get_logger

logger = get_logger(__name__)


class FileService:
    """Service for file management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_file(
        self,
        file_id: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Optional[File]:
        """Get file by ID"""
        query = select(File).where(
            File.file_id == file_id,
            File.is_deleted == False
        )
        
        if guest_token:
            query = query.where(File.guest_token == guest_token)
        elif user_id:
            query = query.where(File.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_file_download_path(
        self,
        file_id: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Optional[Path]:
        """Get file path for download"""
        file = await self.get_file(file_id, guest_token, user_id)
        
        if not file:
            return None
        
        # Check if expired
        if file.expires_at < datetime.utcnow():
            return None
        
        file_path = Path(file.file_path)
        if not file_path.exists():
            return None
        
        return file_path
    
    async def track_download(self, file_id: str):
        """Track file download"""
        result = await self.db.execute(
            select(File).where(File.file_id == file_id)
        )
        file = result.scalar_one_or_none()
        
        if file:
            file.download_count += 1
            file.last_downloaded_at = datetime.utcnow()
            await self.db.commit()
    
    async def delete_file(
        self,
        file_id: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> bool:
        """Mark file as deleted"""
        file = await self.get_file(file_id, guest_token, user_id)
        
        if not file:
            return False
        
        file.is_deleted = True
        file.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
