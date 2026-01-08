"""
Tool service - handles file processing operations
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from app.models.models import Job, File, JobStatus, FileType
from app.core.config import settings
from app.core.logging import get_logger
from app.workers.tasks import (
    merge_pdfs_task, split_pdf_task, compress_pdf_task,
    convert_pdf_to_word_task, convert_word_to_pdf_task,
    convert_pdf_to_images_task, convert_images_to_pdf_task,
    convert_image_format_task
)

logger = get_logger(__name__)


class ToolService:
    """Service for file processing tools"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def upload_files(
        self,
        files: List[UploadFile],
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[str]:
        """
        Upload files and store metadata
        
        Args:
            files: List of uploaded files
            guest_token: Optional guest token
            user_id: Optional user ID
            
        Returns:
            List of file IDs
        """
        file_ids = []
        
        for upload_file in files:
            # Validate file size
            content = await upload_file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise ValueError(f"File {upload_file.filename} exceeds maximum size")
            
            # Generate unique file ID and path
            file_id = str(uuid.uuid4())
            file_ext = Path(upload_file.filename).suffix
            stored_filename = f"{file_id}{file_ext}"
            file_path = settings.UPLOAD_DIR / stored_filename
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Determine file type
            file_type = self._determine_file_type(upload_file.content_type)
            
            # Create file record
            file_record = File(
                file_id=file_id,
                original_filename=upload_file.filename,
                stored_filename=stored_filename,
                file_path=str(file_path),
                file_size=len(content),
                file_type=file_type,
                mime_type=upload_file.content_type or "application/octet-stream",
                checksum="",  # TODO: Calculate checksum
                user_id=user_id,
                guest_token=guest_token,
                is_input=True,
                expires_at=datetime.utcnow() + timedelta(hours=settings.FILE_TTL_HOURS)
            )
            
            self.db.add(file_record)
            file_ids.append(file_id)
        
        await self.db.commit()
        return file_ids
    
    def _determine_file_type(self, mime_type: str) -> FileType:
        """Determine file type from MIME type"""
        if "pdf" in mime_type.lower():
            return FileType.PDF
        elif "word" in mime_type.lower() or "document" in mime_type.lower():
            return FileType.WORD
        elif "excel" in mime_type.lower() or "spreadsheet" in mime_type.lower():
            return FileType.EXCEL
        elif "image" in mime_type.lower():
            return FileType.IMAGE
        else:
            return FileType.OTHER
    
    async def _create_job(
        self,
        tool_name: str,
        input_files_count: int,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Job:
        """Create a new job"""
        job_id = str(uuid.uuid4())
        
        job = Job(
            job_id=job_id,
            tool_name=tool_name,
            status=JobStatus.PENDING,
            user_id=user_id,
            guest_token=guest_token,
            input_files_count=input_files_count,
            expires_at=datetime.utcnow() + timedelta(hours=settings.FILE_TTL_HOURS)
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        return job
    
    async def merge_pdfs(
        self,
        file_ids: List[str],
        output_filename: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Job:
        """Create PDF merge job"""
        job = await self._create_job(
            "pdf_merge",
            len(file_ids),
            guest_token,
            user_id
        )
        
        # Queue background task
        merge_pdfs_task.delay(job.job_id, file_ids, output_filename)
        
        return job
    
    async def split_pdf(
        self,
        file_id: str,
        split_type: str,
        pages: Optional[List[int]],
        ranges: Optional[List[tuple]],
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Job:
        """Create PDF split job"""
        job = await self._create_job(
            "pdf_split",
            1,
            guest_token,
            user_id
        )
        
        split_pdf_task.delay(job.job_id, file_id, split_type, pages, ranges)
        
        return job
    
    async def compress_pdf(
        self,
        file_id: str,
        compression_level: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Job:
        """Create PDF compress job"""
        job = await self._create_job(
            "pdf_compress",
            1,
            guest_token,
            user_id
        )
        
        compress_pdf_task.delay(job.job_id, file_id, compression_level)
        
        return job
    
    async def convert_pdf_to_word(
        self,
        file_id: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Job:
        """Create PDF to Word conversion job"""
        job = await self._create_job(
            "pdf_to_word",
            1,
            guest_token,
            user_id
        )
        
        convert_pdf_to_word_task.delay(job.job_id, file_id)
        
        return job
    
    async def convert_word_to_pdf(
        self,
        file_id: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Job:
        """Create Word to PDF conversion job"""
        job = await self._create_job(
            "word_to_pdf",
            1,
            guest_token,
            user_id
        )
        
        convert_word_to_pdf_task.delay(job.job_id, file_id)
        
        return job
    
    async def convert_pdf_to_images(
        self,
        file_id: str,
        output_format: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Job:
        """Create PDF to images conversion job"""
        job = await self._create_job(
            "pdf_to_images",
            1,
            guest_token,
            user_id
        )
        
        convert_pdf_to_images_task.delay(job.job_id, file_id, output_format)
        
        return job
    
    async def convert_images_to_pdf(
        self,
        file_ids: List[str],
        output_filename: str,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Job:
        """Create images to PDF conversion job"""
        job = await self._create_job(
            "images_to_pdf",
            len(file_ids),
            guest_token,
            user_id
        )
        
        convert_images_to_pdf_task.delay(job.job_id, file_ids, output_filename)
        
        return job
    
    async def convert_image_format(
        self,
        file_id: str,
        output_format: str,
        quality: int,
        width: Optional[int],
        height: Optional[int],
        maintain_aspect_ratio: bool,
        guest_token: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Job:
        """Create image format conversion job"""
        job = await self._create_job(
            "image_convert",
            1,
            guest_token,
            user_id
        )
        
        convert_image_format_task.delay(
            job.job_id, file_id, output_format,
            quality, width, height, maintain_aspect_ratio
        )
        
        return job
