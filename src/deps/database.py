"""
Database Deps.

Author : Coke
Date   : 2025-03-29
"""

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing_extensions import Annotated, Doc

from src.core.config import settings
from src.core.database import AsyncRedisClient, RedisManager, get_async_session

__all__ = [
    "SessionDep",
    "RedisDep",
]

SessionDep = Annotated[
    AsyncSession,
    Depends(get_async_session),
    Doc(
        """
        This dependency is used to provide an instance of `AsyncSession` for database operations.
        The session is obtained from the `get_async_session`, which manages the lifecycle of the database session.
        """
    ),
]


async def get_redis_client() -> AsyncRedisClient:
    """
    Returns an instance of AsyncRedisClient using the current Redis client.

    Returns:
        AsyncRedisClient: The Redis client instance.
    """
    client = RedisManager.client()
    return AsyncRedisClient(client=client, echo=settings.ENVIRONMENT.is_debug)


RedisDep = Annotated[
    AsyncRedisClient,
    Depends(get_redis_client),
    Doc(
        """
        This dependency provides an instance of `AsyncRedisClient`, which allows interaction with a Redis database.
        The client is obtained from the `get_redis_client`, which manages the lifecycle of the Redis connection.
        """
    ),
]
