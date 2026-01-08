"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


# Enums
class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileType(str, Enum):
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    IMAGE = "image"
    OTHER = "other"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator("password")
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[datetime] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# File Schemas
class FileUpload(BaseModel):
    """Schema for file upload metadata"""
    filename: str
    size: int
    mime_type: str


class FileResponse(BaseModel):
    id: int
    file_id: str
    original_filename: str
    file_size: int
    file_type: FileType
    mime_type: str
    storage_url: Optional[str]
    created_at: datetime
    expires_at: datetime
    download_count: int
    
    class Config:
        from_attributes = True


# Job Schemas
class JobCreate(BaseModel):
    tool_name: str
    input_files_count: int = 1


class JobResponse(BaseModel):
    id: int
    job_id: str
    tool_name: str
    status: JobStatus
    progress: int
    input_files_count: int
    output_file_id: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    processing_time_seconds: Optional[float]
    
    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    result_url: Optional[str] = None
    error_message: Optional[str] = None


# Tool Schemas
class PDFMergeRequest(BaseModel):
    """Request to merge multiple PDFs"""
    files: List[str] = Field(..., min_items=2, max_items=50)
    output_filename: Optional[str] = "merged.pdf"


class PDFSplitRequest(BaseModel):
    """Request to split a PDF"""
    file_id: str
    split_type: str = Field(..., description="'pages' or 'ranges'")
    pages: Optional[List[int]] = Field(None, description="List of page numbers for 'pages' mode")
    ranges: Optional[List[tuple]] = Field(None, description="List of (start, end) tuples for 'ranges' mode")


class PDFCompressRequest(BaseModel):
    """Request to compress a PDF"""
    file_id: str
    compression_level: str = Field("medium", description="'low', 'medium', 'high'")


class ConversionRequest(BaseModel):
    """Generic conversion request"""
    file_id: str
    output_format: str
    options: Optional[dict] = {}


class ImageConversionRequest(BaseModel):
    """Image conversion request"""
    file_id: str
    output_format: str = Field(..., description="'png', 'jpg', 'webp', etc.")
    quality: Optional[int] = Field(90, ge=1, le=100)
    width: Optional[int] = None
    height: Optional[int] = None
    maintain_aspect_ratio: bool = True


# Response Schemas
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    database: str
    redis: str


# Dashboard Schemas
class UserDashboard(BaseModel):
    user: UserResponse
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_files_processed: int
    storage_used_mb: float
    recent_jobs: List[JobResponse]


class JobHistory(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
