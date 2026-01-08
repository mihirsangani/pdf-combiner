"""
Job service - handles job status and management
"""
from typing import Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.models import Job, JobStatus
from app.schemas.schemas import JobStatusResponse, JobHistory
from app.core.logging import get_logger

logger = get_logger(__name__)


class JobService:
    """Service for job management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_job(
        self,
        job_id: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Optional[Job]:
        """Get job by ID"""
        query = select(Job).where(Job.job_id == job_id)
        
        if guest_token:
            query = query.where(Job.guest_token == guest_token)
        elif user_id:
            query = query.where(Job.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_job_status(
        self,
        job_id: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Optional[JobStatusResponse]:
        """Get simplified job status"""
        job = await self.get_job(job_id, guest_token, user_id)
        
        if not job:
            return None
        
        result_url = None
        if job.status == JobStatus.COMPLETED and job.output_file_id:
            result_url = f"/api/v1/files/{job.output_file_id}/download"
        
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            result_url=result_url,
            error_message=job.error_message
        )
    
    async def cancel_job(
        self,
        job_id: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> bool:
        """Cancel a job"""
        job = await self.get_job(job_id, guest_token, user_id)
        
        if not job or job.status not in [JobStatus.PENDING, JobStatus.PROCESSING]:
            return False
        
        job.status = JobStatus.CANCELLED
        job.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def get_job_history(
        self,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> JobHistory:
        """Get job history"""
        query = select(Job).order_by(desc(Job.created_at))
        
        if guest_token:
            query = query.where(Job.guest_token == guest_token)
        elif user_id:
            query = query.where(Job.user_id == user_id)
        
        # Get total count
        count_result = await self.db.execute(query)
        total = len(count_result.all())
        
        # Paginate
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        jobs = result.scalars().all()
        
        return JobHistory(
            jobs=list(jobs),
            total=total,
            page=page,
            page_size=page_size,
            has_more=offset + len(jobs) < total
        )
    
    async def update_job_progress(
        self,
        job_id: str,
        progress: int,
        status: Optional[JobStatus] = None
    ):
        """Update job progress"""
        result = await self.db.execute(
            select(Job).where(Job.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if job:
            job.progress = progress
            if status:
                job.status = status
            job.updated_at = datetime.utcnow()
            
            await self.db.commit()
