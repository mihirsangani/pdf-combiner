"""
Celery background tasks for file processing
"""
from celery import Task
from typing import List, Optional
from pathlib import Path
import PyPDF2
from PIL import Image
from pdf2image import convert_from_path
import subprocess
from datetime import datetime

from app.workers.celery_app import celery_app
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseTask(Task):
    """Base task with database session"""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            from app.db.session import AsyncSessionLocal
            self._db = AsyncSessionLocal()
        return self._db


@celery_app.task(bind=True, base=DatabaseTask)
def merge_pdfs_task(
    self,
    job_id: str,
    file_ids: List[str],
    output_filename: str
):
    """
    Merge multiple PDF files
    
    Args:
        job_id: Job ID
        file_ids: List of file IDs to merge
        output_filename: Output filename
    """
    try:
        logger.info("Starting PDF merge", job_id=job_id, file_count=len(file_ids))
        
        # Update job status
        update_job_status(job_id, "processing", 10)
        
        # Get file paths
        file_paths = get_file_paths(file_ids)
        
        # Merge PDFs
        merger = PyPDF2.PdfMerger()
        
        for i, file_path in enumerate(file_paths):
            merger.append(str(file_path))
            progress = 10 + int((i + 1) / len(file_paths) * 70)
            update_job_status(job_id, "processing", progress)
        
        # Save merged PDF
        output_path = settings.UPLOAD_DIR / output_filename
        merger.write(str(output_path))
        merger.close()
        
        # Create output file record
        output_file_id = create_output_file(
            job_id,
            output_path,
            output_filename,
            "application/pdf"
        )
        
        # Update job as completed
        update_job_status(job_id, "completed", 100, output_file_id)
        
        logger.info("PDF merge completed", job_id=job_id)
        
    except Exception as e:
        logger.error("PDF merge failed", job_id=job_id, error=str(e))
        update_job_status(job_id, "failed", 0, error_message=str(e))


@celery_app.task(bind=True, base=DatabaseTask)
def split_pdf_task(
    self,
    job_id: str,
    file_id: str,
    split_type: str,
    pages: Optional[List[int]],
    ranges: Optional[List[tuple]]
):
    """
    Split PDF file
    
    Args:
        job_id: Job ID
        file_id: File ID to split
        split_type: 'pages' or 'ranges'
        pages: List of page numbers
        ranges: List of (start, end) tuples
    """
    try:
        logger.info("Starting PDF split", job_id=job_id)
        
        update_job_status(job_id, "processing", 10)
        
        # Get file path
        file_path = get_file_paths([file_id])[0]
        
        # Read PDF
        reader = PyPDF2.PdfReader(str(file_path))
        total_pages = len(reader.pages)
        
        if split_type == "pages" and pages:
            # Extract specific pages
            writer = PyPDF2.PdfWriter()
            for page_num in pages:
                if 0 <= page_num < total_pages:
                    writer.add_page(reader.pages[page_num])
            
            output_path = settings.UPLOAD_DIR / f"split_{file_id}.pdf"
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            output_file_id = create_output_file(
                job_id,
                output_path,
                output_path.name,
                "application/pdf"
            )
        
        update_job_status(job_id, "completed", 100, output_file_id)
        logger.info("PDF split completed", job_id=job_id)
        
    except Exception as e:
        logger.error("PDF split failed", job_id=job_id, error=str(e))
        update_job_status(job_id, "failed", 0, error_message=str(e))


@celery_app.task(bind=True, base=DatabaseTask)
def compress_pdf_task(
    self,
    job_id: str,
    file_id: str,
    compression_level: str
):
    """
    Compress PDF file
    
    Args:
        job_id: Job ID
        file_id: File ID to compress
        compression_level: 'low', 'medium', or 'high'
    """
    try:
        logger.info("Starting PDF compression", job_id=job_id)
        
        update_job_status(job_id, "processing", 10)
        
        file_path = get_file_paths([file_id])[0]
        output_path = settings.UPLOAD_DIR / f"compressed_{file_id}.pdf"
        
        # Use Ghostscript for compression
        quality_settings = {
            "low": "/screen",
            "medium": "/ebook",
            "high": "/printer"
        }
        
        gs_quality = quality_settings.get(compression_level, "/ebook")
        
        subprocess.run([
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={gs_quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            str(file_path)
        ], check=True)
        
        output_file_id = create_output_file(
            job_id,
            output_path,
            output_path.name,
            "application/pdf"
        )
        
        update_job_status(job_id, "completed", 100, output_file_id)
        logger.info("PDF compression completed", job_id=job_id)
        
    except Exception as e:
        logger.error("PDF compression failed", job_id=job_id, error=str(e))
        update_job_status(job_id, "failed", 0, error_message=str(e))


@celery_app.task(bind=True, base=DatabaseTask)
def convert_pdf_to_word_task(self, job_id: str, file_id: str):
    """Convert PDF to Word document"""
    try:
        logger.info("Starting PDF to Word conversion", job_id=job_id)
        update_job_status(job_id, "processing", 10)
        
        file_path = get_file_paths([file_id])[0]
        output_path = settings.UPLOAD_DIR / f"{file_id}.docx"
        
        # Use LibreOffice for conversion
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "docx",
            "--outdir",
            str(settings.UPLOAD_DIR),
            str(file_path)
        ], check=True)
        
        output_file_id = create_output_file(
            job_id,
            output_path,
            output_path.name,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        update_job_status(job_id, "completed", 100, output_file_id)
        logger.info("PDF to Word conversion completed", job_id=job_id)
        
    except Exception as e:
        logger.error("PDF to Word conversion failed", job_id=job_id, error=str(e))
        update_job_status(job_id, "failed", 0, error_message=str(e))


@celery_app.task(bind=True, base=DatabaseTask)
def convert_word_to_pdf_task(self, job_id: str, file_id: str):
    """Convert Word document to PDF"""
    try:
        logger.info("Starting Word to PDF conversion", job_id=job_id)
        update_job_status(job_id, "processing", 10)
        
        file_path = get_file_paths([file_id])[0]
        output_path = settings.UPLOAD_DIR / f"{file_id}.pdf"
        
        # Use LibreOffice for conversion
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(settings.UPLOAD_DIR),
            str(file_path)
        ], check=True)
        
        output_file_id = create_output_file(
            job_id,
            output_path,
            output_path.name,
            "application/pdf"
        )
        
        update_job_status(job_id, "completed", 100, output_file_id)
        logger.info("Word to PDF conversion completed", job_id=job_id)
        
    except Exception as e:
        logger.error("Word to PDF conversion failed", job_id=job_id, error=str(e))
        update_job_status(job_id, "failed", 0, error_message=str(e))


@celery_app.task(bind=True, base=DatabaseTask)
def convert_pdf_to_images_task(
    self,
    job_id: str,
    file_id: str,
    output_format: str
):
    """Convert PDF pages to images"""
    try:
        logger.info("Starting PDF to images conversion", job_id=job_id)
        update_job_status(job_id, "processing", 10)
        
        file_path = get_file_paths([file_id])[0]
        
        # Convert PDF to images
        images = convert_from_path(str(file_path))
        
        # Save images as ZIP
        import zipfile
        output_path = settings.UPLOAD_DIR / f"{file_id}_images.zip"
        
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for i, image in enumerate(images):
                img_path = settings.TEMP_DIR / f"page_{i+1}.{output_format}"
                image.save(str(img_path), output_format.upper())
                zipf.write(img_path, f"page_{i+1}.{output_format}")
                img_path.unlink()
        
        output_file_id = create_output_file(
            job_id,
            output_path,
            output_path.name,
            "application/zip"
        )
        
        update_job_status(job_id, "completed", 100, output_file_id)
        logger.info("PDF to images conversion completed", job_id=job_id)
        
    except Exception as e:
        logger.error("PDF to images conversion failed", job_id=job_id, error=str(e))
        update_job_status(job_id, "failed", 0, error_message=str(e))


@celery_app.task(bind=True, base=DatabaseTask)
def convert_images_to_pdf_task(
    self,
    job_id: str,
    file_ids: List[str],
    output_filename: str
):
    """Convert images to PDF"""
    try:
        logger.info("Starting images to PDF conversion", extra={
            "job_id": job_id,
            "file_count": len(file_ids),
            "output_filename": output_filename
        })
        update_job_status(job_id, "processing", 10)
        logger.info(f"Job {job_id} status updated to processing")
        
        logger.info(f"Retrieving file paths for {len(file_ids)} files", extra={"job_id": job_id})
        file_paths = get_file_paths(file_ids)
        logger.info(f"Retrieved {len(file_paths)} file paths", extra={
            "job_id": job_id,
            "paths": [str(p) for p in file_paths]
        })
        
        # Open images
        logger.info(f"Opening {len(file_paths)} images", extra={"job_id": job_id})
        images = []
        for idx, path in enumerate(file_paths):
            logger.debug(f"Opening image {idx + 1}/{len(file_paths)}: {path}", extra={"job_id": job_id})
            try:
                img = Image.open(str(path))
                logger.debug(f"Image {idx + 1} opened successfully - mode: {img.mode}, size: {img.size}", extra={"job_id": job_id})
                images.append(img)
            except Exception as e:
                logger.error(f"Failed to open image {idx + 1} ({path}): {str(e)}", extra={"job_id": job_id})
                raise
        
        logger.info(f"Successfully opened {len(images)} images", extra={"job_id": job_id})
        update_job_status(job_id, "processing", 30)
        
        # Convert to RGB if necessary
        logger.info("Converting images to RGB mode", extra={"job_id": job_id})
        images_rgb = []
        for idx, img in enumerate(images):
            logger.debug(f"Converting image {idx + 1}/{len(images)} - original mode: {img.mode}", extra={"job_id": job_id})
            if img.mode != 'RGB':
                logger.debug(f"Image {idx + 1} requires conversion from {img.mode} to RGB", extra={"job_id": job_id})
                img = img.convert('RGB')
                logger.debug(f"Image {idx + 1} converted to RGB successfully", extra={"job_id": job_id})
            images_rgb.append(img)
        
        logger.info(f"All {len(images_rgb)} images converted to RGB", extra={"job_id": job_id})
        update_job_status(job_id, "processing", 60)
        
        # Save as PDF
        output_path = settings.UPLOAD_DIR / output_filename
        logger.info(f"Saving PDF to {output_path}", extra={"job_id": job_id})
        try:
            images_rgb[0].save(
                str(output_path),
                save_all=True,
                append_images=images_rgb[1:] if len(images_rgb) > 1 else [],
                format="PDF"
            )
            logger.info(f"PDF saved successfully to {output_path}", extra={
                "job_id": job_id,
                "file_size": output_path.stat().st_size if output_path.exists() else 0
            })
        except Exception as e:
            logger.error(f"Failed to save PDF: {str(e)}", extra={"job_id": job_id})
            raise
        
        update_job_status(job_id, "processing", 80)
        
        logger.info(f"Creating output file record for job {job_id}", extra={"job_id": job_id})
        output_file_id = create_output_file(
            job_id,
            output_path,
            output_filename,
            "application/pdf"
        )
        logger.info(f"Output file record created with ID: {output_file_id}", extra={
            "job_id": job_id,
            "output_file_id": output_file_id
        })
        
        update_job_status(job_id, "completed", 100, output_file_id)
        logger.info("Images to PDF conversion completed successfully", extra={
            "job_id": job_id,
            "output_file_id": output_file_id,
            "output_filename": output_filename
        })
        
    except Exception as e:
        logger.error("Images to PDF conversion failed", extra={
            "job_id": job_id,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        update_job_status(job_id, "failed", 0, error_message=str(e))


@celery_app.task(bind=True, base=DatabaseTask)
def convert_image_format_task(
    self,
    job_id: str,
    file_id: str,
    output_format: str,
    quality: int,
    width: Optional[int],
    height: Optional[int],
    maintain_aspect_ratio: bool
):
    """Convert image format"""
    try:
        logger.info("Starting image conversion", job_id=job_id)
        update_job_status(job_id, "processing", 10)
        
        file_path = get_file_paths([file_id])[0]
        
        # Open image
        image = Image.open(str(file_path))
        
        # Resize if dimensions provided
        if width or height:
            if maintain_aspect_ratio:
                image.thumbnail((width or image.width, height or image.height))
            else:
                image = image.resize((width or image.width, height or image.height))
        
        # Save in new format
        output_path = settings.UPLOAD_DIR / f"{file_id}.{output_format}"
        image.save(str(output_path), output_format.upper(), quality=quality)
        
        output_file_id = create_output_file(
            job_id,
            output_path,
            output_path.name,
            f"image/{output_format}"
        )
        
        update_job_status(job_id, "completed", 100, output_file_id)
        logger.info("Image conversion completed", job_id=job_id)
        
    except Exception as e:
        logger.error("Image conversion failed", job_id=job_id, error=str(e))
        update_job_status(job_id, "failed", 0, error_message=str(e))


@celery_app.task
def cleanup_expired_files():
    """Cleanup expired files (periodic task)"""
    try:
        from app.db.session import AsyncSessionLocal
        from app.models.models import File, Job
        from sqlalchemy import select
        import asyncio
        
        async def cleanup():
            async with AsyncSessionLocal() as db:
                # Get expired files
                result = await db.execute(
                    select(File).where(
                        File.expires_at < datetime.utcnow(),
                        File.is_deleted == False
                    )
                )
                expired_files = result.scalars().all()
                
                for file in expired_files:
                    # Delete physical file
                    file_path = Path(file.file_path)
                    if file_path.exists():
                        file_path.unlink()
                    
                    # Mark as deleted
                    file.is_deleted = True
                
                await db.commit()
                
                logger.info("Cleaned up expired files", count=len(expired_files))
        
        asyncio.run(cleanup())
        
    except Exception as e:
        logger.error("Cleanup task failed", error=str(e))


# Helper functions
def get_file_paths(file_ids: List[str]) -> List[Path]:
    """Get file paths from file IDs"""
    from app.db.session import get_session_local
    from app.models.models import File
    
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        files = db.query(File).filter(File.file_id.in_(file_ids)).all()
        return [Path(f.file_path) for f in files]
    finally:
        db.close()


def update_job_status(
    job_id: str,
    status: str,
    progress: int,
    output_file_id: Optional[str] = None,
    error_message: Optional[str] = None
):
    """Update job status in database"""
    from app.db.session import get_session_local
    from app.models.models import Job, JobStatus
    
    db = None
    try:
        SessionLocal = get_session_local()
        db = SessionLocal()
        
        job = db.query(Job).filter(Job.job_id == job_id).first()
        
        if job:
            job.status = JobStatus(status)
            job.progress = progress
            if output_file_id:
                job.output_file_id = int(output_file_id) if isinstance(output_file_id, str) and output_file_id.isdigit() else output_file_id
            if error_message:
                job.error_message = error_message
            job.updated_at = datetime.utcnow()
            
            if status == "completed":
                job.processing_completed_at = datetime.utcnow()
                if job.processing_started_at:
                    delta = job.processing_completed_at - job.processing_started_at
                    job.processing_time_seconds = delta.total_seconds()
            
            db.commit()
            logger.info(f"Updated job {job_id} status to {status}")
        else:
            logger.warning(f"Job {job_id} not found")
    except Exception as e:
        logger.error(f"Error updating job status: {str(e)}")
    finally:
        if db:
            db.close()


def create_output_file(
    job_id: str,
    file_path: Path,
    filename: str,
    mime_type: str
) -> str:
    """Create output file record"""
    from app.db.session import get_session_local
    from app.models.models import File, Job, FileType
    import uuid
    from datetime import timedelta
    
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        file_id = str(uuid.uuid4())
        file = File(
            file_id=file_id,
            original_filename=filename,
            stored_filename=file_path.name,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            file_type=FileType.PDF if "pdf" in mime_type else FileType.OTHER,
            mime_type=mime_type,
            checksum="",
            user_id=job.user_id,
            guest_token=job.guest_token,
            is_input=False,
            expires_at=datetime.utcnow() + timedelta(hours=settings.FILE_TTL_HOURS)
        )
        
        db.add(file)
        db.commit()
        db.refresh(file)
        
        logger.info(f"Created output file {file.id} for job {job_id}")
        return str(file.id)
    finally:
        db.close()
