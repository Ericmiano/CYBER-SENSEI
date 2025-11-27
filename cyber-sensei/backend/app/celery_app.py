import os
from celery import Celery
from celery.schedules import crontab


def _bool_env(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


broker_url = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND") or broker_url

celery_app = Celery(
    "cyber_sensei",
    broker=broker_url,
    backend=backend_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_always_eager=_bool_env("CELERY_TASK_ALWAYS_EAGER", "false"),
    task_eager_propagates=True,
    # Beat schedule for periodic tasks
    beat_schedule={
        'daily-summaries': {
            'task': 'app.tasks.daily_learning_summary',
            'schedule': crontab(hour=20, minute=0),  # 8 PM daily
        },
        'weekly-reports': {
            'task': 'app.tasks.weekly_progress_report',
            'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Monday 9 AM
        },
        'refresh-recommendations': {
            'task': 'app.tasks.refresh_all_user_recommendations',
            'schedule': crontab(hour='*/6'),  # Every 6 hours
        },
        'cleanup-sessions': {
            'task': 'app.tasks.cleanup_old_sessions',
            'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        },
        'archive-logs': {
            'task': 'app.tasks.archive_old_logs',
            'schedule': crontab(day_of_month=1, hour=3, minute=0),  # Monthly
        },
    }
)

celery_app.autodiscover_tasks(['app'])
celery_app.autodiscover_tasks(["app.services"])

