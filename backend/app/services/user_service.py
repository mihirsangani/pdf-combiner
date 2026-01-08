"""
User service - handles user management
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, Job, File, JobStatus
from app.schemas.schemas import UserUpdate, UserDashboard, UserResponse
from app.core.security import get_password_hash
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_dashboard(self, user_id: int) -> UserDashboard:
        """Get user dashboard statistics"""
        # Get user
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one()
        
        # Get job statistics
        total_jobs_result = await self.db.execute(
            select(func.count(Job.id)).where(Job.user_id == user_id)
        )
        total_jobs = total_jobs_result.scalar() or 0
        
        completed_jobs_result = await self.db.execute(
            select(func.count(Job.id)).where(
                Job.user_id == user_id,
                Job.status == JobStatus.COMPLETED
            )
        )
        completed_jobs = completed_jobs_result.scalar() or 0
        
        failed_jobs_result = await self.db.execute(
            select(func.count(Job.id)).where(
                Job.user_id == user_id,
                Job.status == JobStatus.FAILED
            )
        )
        failed_jobs = failed_jobs_result.scalar() or 0
        
        # Get file statistics
        files_result = await self.db.execute(
            select(func.sum(File.file_size)).where(File.user_id == user_id)
        )
        total_storage = files_result.scalar() or 0
        storage_used_mb = total_storage / (1024 * 1024)
        
        # Get recent jobs
        recent_jobs_result = await self.db.execute(
            select(Job)
            .where(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
            .limit(10)
        )
        recent_jobs = recent_jobs_result.scalars().all()
        
        return UserDashboard(
            user=UserResponse.from_orm(user),
            total_jobs=total_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            total_files_processed=total_jobs,
            storage_used_mb=storage_used_mb,
            recent_jobs=list(recent_jobs)
        )
    
    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate
    ) -> User:
        """Update user profile"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        
        if user_update.email:
            user.email = user_update.email
        if user_update.username:
            user.username = user_update.username
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        if user_update.password:
            user.hashed_password = get_password_hash(user_update.password)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int):
        """Delete user and all associated data"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        
        # Soft delete - just deactivate
        user.is_active = False
        
        await self.db.commit()
