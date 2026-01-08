"""
Core configuration module using Pydantic Settings V2
Handles all environment variables and application configuration
"""
from typing import List, Optional, Any, Union
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable loading"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "FileForge"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: Union[List[str], str] = ["localhost", "127.0.0.1"]
    
    @model_validator(mode="before")
    @classmethod
    def parse_string_lists(cls, values: Any) -> Any:
        """Parse comma-separated strings into lists"""
        if isinstance(values, dict):
            # Parse CORS_ORIGINS
            if "CORS_ORIGINS" in values and isinstance(values["CORS_ORIGINS"], str):
                values["CORS_ORIGINS"] = [origin.strip() for origin in values["CORS_ORIGINS"].split(",")]
            
            # Parse ALLOWED_HOSTS
            if "ALLOWED_HOSTS" in values and isinstance(values["ALLOWED_HOSTS"], str):
                values["ALLOWED_HOSTS"] = [host.strip() for host in values["ALLOWED_HOSTS"].split(",")]
        
        return values
    
    # Database
    DATABASE_URL: str
    POSTGRES_USER: str = "fileforge"
    POSTGRES_PASSWORD: str = "fileforge_dev_pass"
    POSTGRES_DB: str = "fileforge"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    
    # File Storage
    STORAGE_TYPE: str = "local"  # local or s3
    UPLOAD_DIR: Path = Path("./uploads")
    TEMP_DIR: Path = Path("./temp")
    FILE_TTL_HOURS: int = 24
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: str = "noreply@fileforge.com"
    EMAILS_FROM_NAME: str = "FileForge"
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_PROMETHEUS: bool = True
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic"""
        return self.DATABASE_URL.replace("+asyncpg", "")
    
    def create_upload_dirs(self):
        """Create upload and temp directories if they don't exist"""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Create required directories on startup
settings.create_upload_dirs()
