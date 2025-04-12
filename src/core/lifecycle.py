"""
FastAPI lifecycle.

Author : Coke
Date   : 2025-03-17
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.core.config import settings
from src.core.database import MongoManager, RedisManager

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """
    FastAPI lifecycle.
    Args:
        _app: FastAPI application.
    """
    RedisManager.connect()
    RedisManager.connect(redis_url=str(settings.CELERY_REDIS_URL), pool_name="celery")
    await MongoManager.connect()
    logger.info("Application startup complete.")
    yield

    await RedisManager.clear()
    MongoManager.disconnect()
    logger.info("Application shutdown complete.")
