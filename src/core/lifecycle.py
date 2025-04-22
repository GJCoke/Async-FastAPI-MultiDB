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
from src.core.permission import store_router_in_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    FastAPI lifecycle.
    Args:
        app: FastAPI application.
    """

    RedisManager.connect()
    RedisManager.connect(redis_url=str(settings.CELERY_REDIS_URL), pool_name="celery")

    await MongoManager.connect()
    logger.info("Application startup complete.")

    await store_router_in_db(app.routes)

    yield

    await RedisManager.clear()

    MongoManager.disconnect()
    logger.info("Application shutdown complete.")
