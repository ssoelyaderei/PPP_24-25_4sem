from celery import Celery

celery = Celery(
    "binarizer",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Явный импорт модуля с задачами ─ самый простой способ
import app.celery.tasks          # noqa: E402,F401



