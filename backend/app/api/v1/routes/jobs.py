"""
Job status and management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.base import get_db
from app.schemas.schemas import JobResponse, JobStatusResponse, JobHistory
from app.services.job_service import JobService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get job status and details
    
    - **job_id**: Job ID returned from tool endpoints
    - **guest_token**: Optional guest token for guest users
    """
    job_service = JobService(db)
    
    job = await job_service.get_job(job_id, guest_token)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status_simple(
    job_id: str,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get simplified job status (polling-friendly)
    """
    job_service = JobService(db)
    
    status_info = await job_service.get_job_status(job_id, guest_token)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return status_info


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a pending or processing job
    """
    job_service = JobService(db)
    
    success = await job_service.cancel_job(job_id, guest_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be cancelled"
        )
    
    logger.info("Job cancelled", job_id=job_id)
    return {
        "success": True,
        "message": "Job cancelled successfully"
    }


@router.get("/history", response_model=JobHistory)
async def get_job_history(
    page: int = 1,
    page_size: int = 20,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get job history (requires authentication or guest token)
    """
    job_service = JobService(db)
    
    history = await job_service.get_job_history(
        guest_token,
        page,
        page_size
    )
    
    return history
