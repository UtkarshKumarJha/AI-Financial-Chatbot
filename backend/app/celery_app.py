import os
from celery import Celery

BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672/")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

app = Celery(
    "financial_chatbot",
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=["app.tasks"]
    )

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)