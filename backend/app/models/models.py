"""
Database models for the application
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Integer, Boolean, DateTime, Text, 
    Enum as SQLEnum, ForeignKey, Index, BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from ..db.base import Base


class UserRole(str, PyEnum):
    """User role enumeration"""
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class JobStatus(str, PyEnum):
    """Job processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileType(str, PyEnum):
    """Supported file types"""
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    IMAGE = "image"
    OTHER = "other"


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # User status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)
    
    # OAuth
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    files: Mapped[list["File"]] = relationship("File", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_oauth", "oauth_provider", "oauth_id"),
    )
    
    def __repr__(self):
        return f"<User {self.email}>"


class Job(Base):
    """Job model for tracking file processing tasks"""
    __tablename__ = "jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    # Job details
    tool_name: Mapped[str] = mapped_column(String(100), index=True)  # e.g., "pdf_merge", "pdf_split"
    status: Mapped[JobStatus] = mapped_column(SQLEnum(JobStatus), default=JobStatus.PENDING, index=True)
    
    # User association (nullable for guest users)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    guest_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Processing details
    input_files_count: Mapped[int] = mapped_column(Integer, default=0)
    output_file_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("files.id"), nullable=True)
    
    # Progress tracking
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Processing metadata
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="jobs")
    output_file: Mapped[Optional["File"]] = relationship("File", foreign_keys=[output_file_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_job_status_created", "status", "created_at"),
        Index("idx_job_expires", "expires_at"),
        Index("idx_job_user_created", "user_id", "created_at"),
    )
    
    def __repr__(self):
        return f"<Job {self.job_id} - {self.status}>"


class File(Base):
    """File model for tracking uploaded and generated files"""
    __tablename__ = "files"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    # File details
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    
    # File metadata
    file_size: Mapped[int] = mapped_column(BigInteger)  # Size in bytes
    file_type: Mapped[FileType] = mapped_column(SQLEnum(FileType))
    mime_type: Mapped[str] = mapped_column(String(100))
    checksum: Mapped[str] = mapped_column(String(64))  # SHA256 hash
    
    # User association (nullable for guest users)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    guest_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # File status
    is_input: Mapped[bool] = mapped_column(Boolean, default=True)  # Input or output file
    is_temporary: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Storage
    storage_type: Mapped[str] = mapped_column(String(20), default="local")  # local or s3
    storage_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Download tracking
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    last_downloaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="files")
    
    # Indexes
    __table_args__ = (
        Index("idx_file_expires", "expires_at", "is_deleted"),
        Index("idx_file_user_created", "user_id", "created_at"),
        Index("idx_file_checksum", "checksum"),
    )
    
    def __repr__(self):
        return f"<File {self.original_filename}>"


class ApiKey(Base):
    """API key model for API access"""
    __tablename__ = "api_keys"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # User association
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # Key status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Rate limiting
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<ApiKey {self.name}>"
