"""
Celery application configuration
"""
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "fileforge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.workers.tasks.*": {"queue": "celery"}
    }
)

# Celery beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-files": {
        "task": "app.workers.tasks.cleanup_expired_files",
        "schedule": 3600.0,  # Run every hour
    },
}
