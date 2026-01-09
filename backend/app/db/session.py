"""
Database session management and base configuration
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create synchronous engine for Celery tasks (lazy loading)
_sync_engine = None

def get_sync_engine():
    """Get or create synchronous engine for Celery tasks"""
    global _sync_engine
    if _sync_engine is None:
        from sqlalchemy import create_engine as create_sync_engine
        # Use the async URL but create a synchronous connection
        sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        _sync_engine = create_sync_engine(
            sync_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _sync_engine

# Create synchronous session factory (lazy loading)
def get_session_local():
    """Get SessionLocal class"""
    global SessionLocal
    if SessionLocal is None:
        from sqlalchemy.orm import sessionmaker as create_sessionmaker
        SessionLocal = create_sessionmaker(
            bind=get_sync_engine(),
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return SessionLocal

SessionLocal = None

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    
    Yields:
        AsyncSession instance
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Database session error", error=str(e))
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
