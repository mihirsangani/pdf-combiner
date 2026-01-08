"""
File processing tools routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.base import get_db
from app.schemas.schemas import (
    JobResponse, PDFMergeRequest, PDFSplitRequest,
    PDFCompressRequest, ConversionRequest, ImageConversionRequest
)
from app.services.tool_service import ToolService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/upload", response_model=dict)
async def upload_files(
    files: List[UploadFile] = File(...),
    guest_token: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload files for processing
    
    Returns file IDs for use in tool operations
    """
    tool_service = ToolService(db)
    
    try:
        file_ids = await tool_service.upload_files(files, guest_token)
        logger.info("Files uploaded", count=len(file_ids))
        
        return {
            "success": True,
            "file_ids": file_ids,
            "count": len(file_ids)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/pdf/merge", response_model=JobResponse)
async def merge_pdfs(
    request: PDFMergeRequest,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Merge multiple PDF files into one
    
    - **files**: List of file IDs (2-50 files)
    - **output_filename**: Optional custom output filename
    """
    tool_service = ToolService(db)
    
    try:
        job = await tool_service.merge_pdfs(
            request.files,
            request.output_filename,
            guest_token
        )
        logger.info("PDF merge job created", job_id=job.job_id)
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/pdf/split", response_model=JobResponse)
async def split_pdf(
    request: PDFSplitRequest,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Split a PDF file
    
    - **file_id**: ID of the PDF file
    - **split_type**: 'pages' or 'ranges'
    - **pages**: List of page numbers (for 'pages' mode)
    - **ranges**: List of (start, end) tuples (for 'ranges' mode)
    """
    tool_service = ToolService(db)
    
    try:
        job = await tool_service.split_pdf(
            request.file_id,
            request.split_type,
            request.pages,
            request.ranges,
            guest_token
        )
        logger.info("PDF split job created", job_id=job.job_id)
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/pdf/compress", response_model=JobResponse)
async def compress_pdf(
    request: PDFCompressRequest,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Compress a PDF file
    
    - **file_id**: ID of the PDF file
    - **compression_level**: 'low', 'medium', or 'high'
    """
    tool_service = ToolService(db)
    
    try:
        job = await tool_service.compress_pdf(
            request.file_id,
            request.compression_level,
            guest_token
        )
        logger.info("PDF compress job created", job_id=job.job_id)
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/convert/pdf-to-word", response_model=JobResponse)
async def pdf_to_word(
    request: ConversionRequest,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert PDF to Word document
    """
    tool_service = ToolService(db)
    
    try:
        job = await tool_service.convert_pdf_to_word(
            request.file_id,
            guest_token
        )
        logger.info("PDF to Word job created", job_id=job.job_id)
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/convert/word-to-pdf", response_model=JobResponse)
async def word_to_pdf(
    request: ConversionRequest,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert Word document to PDF
    """
    tool_service = ToolService(db)
    
    try:
        job = await tool_service.convert_word_to_pdf(
            request.file_id,
            guest_token
        )
        logger.info("Word to PDF job created", job_id=job.job_id)
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/convert/pdf-to-image", response_model=JobResponse)
async def pdf_to_image(
    request: ConversionRequest,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert PDF pages to images
    """
    tool_service = ToolService(db)
    
    try:
        job = await tool_service.convert_pdf_to_images(
            request.file_id,
            request.output_format,
            guest_token
        )
        logger.info("PDF to images job created", job_id=job.job_id)
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/convert/image-to-pdf", response_model=JobResponse)
async def images_to_pdf(
    request: PDFMergeRequest,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert images to PDF
    """
    tool_service = ToolService(db)
    
    try:
        job = await tool_service.convert_images_to_pdf(
            request.files,
            request.output_filename,
            guest_token
        )
        logger.info("Images to PDF job created", job_id=job.job_id)
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/image/convert", response_model=JobResponse)
async def convert_image(
    request: ImageConversionRequest,
    guest_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert image format
    
    - **file_id**: ID of the image file
    - **output_format**: Target format (png, jpg, webp, etc.)
    - **quality**: Image quality (1-100, default 90)
    - **width**: Optional target width
    - **height**: Optional target height
    - **maintain_aspect_ratio**: Maintain aspect ratio when resizing
    """
    tool_service = ToolService(db)
    
    try:
        job = await tool_service.convert_image_format(
            request.file_id,
            request.output_format,
            request.quality,
            request.width,
            request.height,
            request.maintain_aspect_ratio,
            guest_token
        )
        logger.info("Image conversion job created", job_id=job.job_id)
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/available")
async def get_available_tools():
    """
    Get list of available tools
    """
    return {
        "tools": [
            {
                "id": "pdf_merge",
                "name": "Merge PDFs",
                "description": "Combine multiple PDF files into one",
                "category": "pdf"
            },
            {
                "id": "pdf_split",
                "name": "Split PDF",
                "description": "Split a PDF into multiple files",
                "category": "pdf"
            },
            {
                "id": "pdf_compress",
                "name": "Compress PDF",
                "description": "Reduce PDF file size",
                "category": "pdf"
            },
            {
                "id": "pdf_to_word",
                "name": "PDF to Word",
                "description": "Convert PDF to Word document",
                "category": "conversion"
            },
            {
                "id": "word_to_pdf",
                "name": "Word to PDF",
                "description": "Convert Word document to PDF",
                "category": "conversion"
            },
            {
                "id": "pdf_to_image",
                "name": "PDF to Image",
                "description": "Convert PDF pages to images",
                "category": "conversion"
            },
            {
                "id": "image_to_pdf",
                "name": "Image to PDF",
                "description": "Convert images to PDF",
                "category": "conversion"
            },
            {
                "id": "image_convert",
                "name": "Convert Image",
                "description": "Convert image format and resize",
                "category": "image"
            }
        ]
    }
