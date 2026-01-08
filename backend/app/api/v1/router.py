"""
API v1 Router - Main router aggregating all API endpoints
"""
from fastapi import APIRouter
from app.api.v1.routes import auth, users, tools, jobs, files

api_router = APIRouter()

# Include all route modules
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    tools.router,
    prefix="/tools",
    tags=["Tools"]
)

api_router.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["Jobs"]
)

api_router.include_router(
    files.router,
    prefix="/files",
    tags=["Files"]
)
