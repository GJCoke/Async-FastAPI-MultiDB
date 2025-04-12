"""
Celery app and config.

Author  : Coke
Date    : 2025-04-10
"""

from src.core.config import settings
from src.queues.celery import Celery

REDIS_URL = str(settings.CELERY_REDIS_URL)
app = Celery("celery_app", broker=REDIS_URL, backend=REDIS_URL)
app.conf.update({"timezone": settings.CELERY_TIMEZONE})

app.autodiscover_tasks(["src.queues.tasks"])

# TODO: this is delete code.
app.conf.update(
    {
        "beat_schedule": {
            "test_beat_task": {
                "task": "src.queues.tasks.tasks.test_celery",
                "schedule": 10,
            }
        }
    }
)
