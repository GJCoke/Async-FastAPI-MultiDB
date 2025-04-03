"""
Database Deps.

Author : Coke
Date   : 2025-03-29
"""

from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.database import AsyncRedisClient, AsyncSessionLocal, RedisManager
from src.crud.base import BaseBeanieCRUD, BaseSQLModelCRUD
from src.models.test import Test, TestDocument


# Dependency function that yields a database session to be used in FastAPI route handlers.
# The 'AsyncSessionLocal' session maker is used to create a session for each request.
async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


# Type alias for the database session dependency.
# def login(session: SessionDep):
SessionDep = Annotated[AsyncSession, Depends(get_db)]


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


async def get_mongo_test() -> BaseBeanieCRUD[TestDocument, TestDocument, TestDocument]:
    # TODO: this is delete code.
    return BaseBeanieCRUD[TestDocument, TestDocument, TestDocument](TestDocument)


MongoTestDep = Annotated[BaseBeanieCRUD[TestDocument, TestDocument, TestDocument], Depends(get_mongo_test)]


async def get_sql_test(session: SessionDep) -> BaseSQLModelCRUD[Test, Test, Test]:
    # TODO: this is delete code.
    return BaseSQLModelCRUD[Test, Test, Test](Test, session=session)


SQLTestDep = Annotated[BaseSQLModelCRUD[Test, Test, Test], Depends(get_sql_test)]
