"""
MySQL Database Configuration.

This file configures the MySQL database connection using SQLAlchemy
and integrates it with FastAPI for asynchronous database operations.

Author : Coke
Date   : 2025-03-17
"""

import importlib
import logging
import pkgutil
from datetime import timedelta
from pathlib import Path

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import ConnectionPool, Redis
from redis.typing import EncodableT, KeyT
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src import models
from src.core.config import settings
from src.models.base import Document

logger = logging.getLogger("app")
DATABASE_URL = str(settings.MYSQL_URL)

# Create an asynchronous SQLAlchemy engine for MySQL connection.
# The 'echo' parameter is set based on the environment debug flag,
# and 'pool_recycle' ensures that database connections are recycled after 60 seconds.
engine = create_async_engine(DATABASE_URL, echo=settings.ENVIRONMENT.is_debug, pool_recycle=60)

# AsyncSessionLocal is the session maker used to create AsyncSession instances.
# 'expire_on_commit=False' prevents SQLAlchemy from automatically expiring objects after commit.
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

REDIS_URL = str(settings.REDIS_URL)


class RedisManager:
    """
    A class to manage Redis connection pool and client.

    This class is responsible for initializing and managing a Redis connection pool,
    providing a Redis client, and ensuring only one instance of the connection pool
    and client is used throughout the application.
    """

    _pool: ConnectionPool | None = None
    _client: Redis | None = None

    @classmethod
    def connect(cls) -> ConnectionPool:
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
    async def close(cls) -> None:
        """Closes the Redis connection pool and client."""
        if cls._pool:
            await cls._pool.disconnect()
            logger.info("Redis connection pool disconnect completed.")
            cls._pool = None
            cls._client = None

    @classmethod
    def client(cls) -> Redis:
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
    """
    A client for interacting with a Redis database using asyncio.

    This class wraps around a Redis client instance and provides asynchronous methods
    for interacting with Redis. It also includes support for logging Redis commands if
    the 'echo' flag is enabled.
    """

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
        key: KeyT,
        value: EncodableT,
        *,
        ttl: int | timedelta | None = None,
        is_transaction: bool = False,
    ) -> None:
        """
        Sets a key-value pair in Redis.

        Args:
            key (KeyT): The key to store in Redis.
            value (EncodableT): The value to store for the key.
            ttl (int | timedelta | None, optional): The time-to-live for the key. Defaults to None.
            is_transaction (bool, optional): Whether to perform this operation as part of a transaction.
        """

        async with self.client.pipeline(transaction=is_transaction) as pipe:
            await pipe.set(key, value)

            if ttl is not None:
                await pipe.expire(key, ttl)

            await pipe.execute()

        self.logger.info(
            'Setting key: "%s" with value: %s in Redis.',
            key,
            value,
        )

    async def get(self, key: KeyT) -> EncodableT:
        """
        Retrieves the value for a given key from Redis.

        Args:
            key (KeyT): The key to retrieve from Redis.

        Returns:
            EncodableT: The value associated with the key.
        """

        response = await self.client.get(key)

        self.logger.info('Attempting to retrieve value for key: "%s" from Redis.', key)
        self.logger.debug('Successfully retrieved value for key "%s": %s', key, response)

        return response

    async def exists(self, *args: KeyT) -> int:
        """
        Checks if a key exists in Redis.

        Args:
            args (KeyT): The key to check.

        Returns:
            int: The key exists number.
        """
        response = await self.client.exists(*args)
        return response

    async def delete(self, *args: KeyT) -> bool:
        """
        Deletes one or more keys from Redis.

        Args:
            args (KeyT): The keys to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """

        response = await self.client.delete(*args)

        self.logger.info("Attempting to delete key(s): %s from Redis.", args)
        if response:
            self.logger.debug("Successfully deleted key(s): %s", args)
        else:
            self.logger.debug("Failed to delete key(s): %s. The key(s) may not exist.", args)

        return bool(response)


def get_document_models() -> list[type[Document]]:
    """
    Dynamically finds all Beanie Document models in the models package.

    This function scans all Python modules within the 'models' package, and collects
    all classes that are subclasses of the 'Document' class (excluding 'Document' itself).
    These classes are then returned as a list of model classes to be used with Beanie.

    Returns:
        list[type[Document]]: A list of Beanie Document model classes.
    """
    document_models = []

    # Get all Python files in the models directory.
    package_path = Path(models.__file__).parent
    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        module = importlib.import_module(f"{models.__name__}.{module_name}")

        # Iterate over all attributes in the module.
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            # Check if the attribute is a subclass of Document (excluding Document itself).
            if isinstance(attr, type) and issubclass(attr, Document) and attr is not Document:
                document_models.append(attr)

    return document_models


class MongoManager:
    """
    Manages MongoDB connections, providing methods for connection, disconnection, and client retrieval.

    This class handles the lifecycle of the MongoDB connection, ensuring that the database is initialized
    when the application starts and properly closed when the application shuts down.
    """

    _client: AsyncIOMotorClient | None = None

    @classmethod
    async def connect(cls) -> None:
        """
        Initializes the MongoDB connection and configures Beanie.

        This method establishes a connection to MongoDB using `AsyncIOMotorClient` and initializes
        the database models with Beanie.

        Raises:
            RuntimeError: If the connection fails.
        """
        cls._client = AsyncIOMotorClient(str(settings.MONGO_URL))
        await init_beanie(
            database=cls._client["beanie_db"],
            document_models=get_document_models(),
        )
        logger.info("Mongo connection initialization completed.")

    @classmethod
    def close(cls) -> None:
        """
        Closes the MongoDB connection.

        If the client is initialized, this method closes the connection and releases resources.
        """
        if cls._client:
            cls._client.close()
            logger.info("Mongo connection disconnect completed.")
            cls._client = None

    @classmethod
    async def client(cls) -> AsyncIOMotorClient:
        """
        Retrieves the MongoDB client instance.

        Returns:
            AsyncIOMotorClient: The initialized MongoDB client instance.

        Raises:
            RuntimeError: If the client is not initialized.
        """
        if cls._client is None:
            raise RuntimeError("Mongo client not initialized.")
        return cls._client
