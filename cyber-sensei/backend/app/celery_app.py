import os

from celery import Celery


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
)

celery_app.autodiscover_tasks(["app.services"])

