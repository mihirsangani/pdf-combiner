"""
File download and management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.base import get_db
from app.schemas.schemas import FileResponse as FileResponseSchema
from app.services.file_service import FileService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/{file_id}", response_model=FileResponseSchema)
async def get_file_info(
    file_id: str,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get file metadata
    """
    file_service = FileService(db)
    
    file_info = await file_service.get_file(file_id, guest_token)
    
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return file_info


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Download a file
    """
    file_service = FileService(db)
    
    file_path = await file_service.get_file_download_path(file_id, guest_token)
    
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or expired"
        )
    
    # Track download
    await file_service.track_download(file_id)
    
    logger.info("File download", file_id=file_id)
    
    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=file_path.name
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a file
    """
    file_service = FileService(db)
    
    success = await file_service.delete_file(file_id, guest_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    logger.info("File deleted", file_id=file_id)
    
    return {
        "success": True,
        "message": "File deleted successfully"
    }
