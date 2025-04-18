"""
Database Deps.

Author : Coke
Date   : 2025-03-29
"""

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.database import AsyncRedisClient, RedisManager, get_async_session

# Type alias for the database session dependency.
# def login(session: SessionDep):
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_redis_client() -> AsyncRedisClient:
    """
    Returns an instance of AsyncRedisClient using the current Redis client.

    Returns:
        AsyncRedisClient: The Redis client instance.
    """
    client = RedisManager.client()
    return AsyncRedisClient(client=client, echo=settings.ENVIRONMENT.is_debug)


# Type alias for the redis client dependency.
RedisClientDep = Annotated[AsyncRedisClient, Depends(get_redis_client)]
