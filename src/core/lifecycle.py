"""
FastAPI lifecycle.

Author : Coke
Date   : 2025-03-17
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.core.database import RedisManager

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """
    FastAPI lifecycle.
    Args:
        _app: FastAPI application.
    """
    RedisManager.init_redis_pool()
    logger.info("Application startup complete.")
    yield

    await RedisManager.close_pool()
    logger.info("Application shutdown complete.")
