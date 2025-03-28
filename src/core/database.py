"""
MySQL Database Configuration.

This file configures the MySQL database connection using SQLAlchemy
and integrates it with FastAPI for asynchronous database operations.

Author : Coke
Date   : 2025-03-17
"""

import logging
from datetime import timedelta
from typing import Annotated, AsyncIterator, Literal, overload

from fastapi import Depends
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.exceptions import NotFoundException

logger = logging.getLogger("app")
DATABASE_URL = str(settings.MYSQL_URL)

# Create an asynchronous SQLAlchemy engine for MySQL connection.
# The 'echo' parameter is set based on the environment debug flag,
# and 'pool_recycle' ensures that database connections are recycled after 60 seconds.
engine = create_async_engine(DATABASE_URL, echo=settings.ENVIRONMENT.is_debug, pool_recycle=60)

# AsyncSessionLocal is the session maker used to create AsyncSession instances.
# 'expire_on_commit=False' prevents SQLAlchemy from automatically expiring objects after commit.
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency function that yields a database session to be used in FastAPI route handlers.
# The 'AsyncSessionLocal' session maker is used to create a session for each request.
async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


# Type alias for the database session dependency.
# def login(session: SessionDep):
SessionDep = Annotated[AsyncSession, Depends(get_db)]

REDIS_URL = str(settings.REDIS_URL)
KeyType = str | bytes | memoryview
ValueType = int | float | KeyType


class RedisManager:
    _pool: ConnectionPool | None = None
    _client: Redis | None = None

    @classmethod
    def init_redis_pool(cls) -> ConnectionPool:
        """
        Initializes the Redis connection pool if it has not been initialized yet.

        Returns:
            ConnectionPool: The initialized Redis connection pool.

        Raises:
            RuntimeError: If Redis connection fails.
        """
        if cls._pool is None:
            cls._pool = ConnectionPool.from_url(
                REDIS_URL, max_connections=settings.REDIS_MAX_CONNECTIONS, decode_responses=True
            )
            cls._client = Redis(connection_pool=cls._pool)
        logger.info("Redis connection pool initialization completed.")
        return cls._pool

    @classmethod
    async def close_pool(cls) -> None:
        """Closes the Redis connection pool and client."""
        if cls._pool:
            await cls._pool.disconnect()
            logger.info("Redis connection pool disconnect completed.")
            cls._pool = None
            cls._client = None

    @classmethod
    def get_client(cls) -> Redis:
        """
        Returns the initialized Redis client.

        This method retrieves the Redis client if it has been initialized. Raises an
        exception if the client has not been set up yet.

        Returns:
            Redis: The initialized Redis client.

        Raises:
            RuntimeError: If the Redis client is not initialized.
        """
        if cls._client is None:
            raise RuntimeError("Redis client not initialized.")
        return cls._client


class AsyncRedisClient:
    def __init__(self, client: Redis, echo: bool = False) -> None:
        """
        Initializes the AsyncRedisClient with a Redis client.

        Args:
            client (Redis): The Redis client to be used.
            echo (bool, optional): Whether to log Redis commands. Defaults to False.

        Attributes:
            client (Redis): The Redis client.
            echo (bool): A flag to control logging of commands.
            logger (logging.Logger): The logger instance for logging Redis operations.
        """
        self._client: Redis = client
        self._echo = echo
        self.logger = logging.getLogger("redis")
        self.logger.setLevel(logging.DEBUG if echo else logging.FATAL)

    @property
    def client(self) -> Redis:
        """
        Returns the Redis client instance.

        Returns:
            Redis: The Redis client.
        """
        return self._client

    @property
    def echo(self) -> bool:
        """
        Returns the echo flag that controls logging.

        Returns:
            bool: The echo flag.
        """
        return self._echo

    async def set(
        self,
        key: KeyType,
        value: ValueType,
        *,
        ttl: int | timedelta | None = None,
        is_transaction: bool = False,
    ) -> None:
        """
        Sets a key-value pair in Redis.

        Args:
            key (KeyType): The key to store in Redis.
            value (ValueType): The value to store for the key.
            ttl (int | timedelta | None, optional): The time-to-live for the key. Defaults to None.
            is_transaction (bool, optional): Whether to perform this operation as part of a transaction.
        """
        self.logger.info(
            "Setting key: %s with value: %s in Redis.",
            key,
            value,
        )

        async with self.client.pipeline(transaction=is_transaction) as pipe:
            await pipe.set(key, value)

            if ttl is not None:
                await pipe.expire(key, ttl)

            await pipe.execute()

    async def get(self, key: KeyType) -> ValueType:
        """
        Retrieves the value for a given key from Redis.

        Args:
            key (KeyType): The key to retrieve from Redis.

        Returns:
            ValueType: The value associated with the key.
        """
        self.logger.info("Attempting to retrieve value for key: %s from Redis.", key)

        response = await self.client.get(key)
        if response is not None:
            self.logger.debug('Successfully retrieved value for key "%s": %s', key, response)
        else:
            self.logger.debug('Key "%s" not found in Redis.', key)

        return response

    @overload
    async def exist(self, key: KeyType, *, nullable: Literal[False]) -> Literal[True]: ...

    @overload
    async def exist(self, key: KeyType, *, nullable: Literal[True]) -> bool: ...

    async def exist(self, key: KeyType, *, nullable: bool = True) -> bool | Literal[True]:
        """
        Checks if a key exists in Redis.

        Args:
            key (KeyType): The key to check.
            nullable (bool, optional): Whether a missing key is allowed. Defaults to True.

        Returns:
            bool: True if the key exists, False otherwise.

        Raises:
            NotFoundException: If the key does not exist and nullable is False.
        """
        response = await self.client.get(key)
        if not nullable and response is None:
            raise NotFoundException(detail="%r not found in redis." % key)

        return response is not None

    async def delete(self, *args: KeyType) -> bool:
        """
        Deletes one or more keys from Redis.

        Args:
            args (KeyType): The keys to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        self.logger.info("Attempting to delete key(s): %s from Redis.", args)

        response = await self.client.delete(*args)

        if response:
            self.logger.debug("Successfully deleted key(s): %s", args)
        else:
            self.logger.debug("Failed to delete key(s): %s. The key(s) may not exist.", args)

        return bool(response)


async def get_redis_client() -> AsyncRedisClient:
    """
    Returns an instance of AsyncRedisClient using the current Redis client.

    Returns:
        AsyncRedisClient: The Redis client instance.
    """
    client = RedisManager.get_client()
    return AsyncRedisClient(client=client, echo=True)


# Type alias for the redis client dependency.
RedisClient = Annotated[AsyncRedisClient, Depends(get_redis_client)]
