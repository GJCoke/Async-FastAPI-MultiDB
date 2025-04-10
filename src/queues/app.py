"""
Author  : Coke
Date    : 2025-04-10
"""

from src.core.config import settings
from src.queues.celery import Celery

REDIS_URL = str(settings.CELERY_REDIS_URL)

app = Celery("celery_app", broker=REDIS_URL, backend=REDIS_URL, beat_schedule={})

app.autodiscover_tasks(["src.queues.tasks"])
