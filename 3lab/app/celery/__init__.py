# app/celery/__init__.py
from celery import Celery
import redislite

# Путь к базе данных Redislite
REDIS_DB_PATH = "/tmp/redis.db"

# Создание экземпляра Redis
redis_server = redislite.Redis(REDIS_DB_PATH)

# Создание экземпляра Celery с именем "celery"
celery = Celery(
    "tasks",  # Имя приложения
    broker=f"redislite://{REDIS_DB_PATH}",  # Брокер
    backend=f"redislite://{REDIS_DB_PATH}"   # Бэкенд
)

# Конфигурация Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)