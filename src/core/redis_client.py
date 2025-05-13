"""
redis file.

Description.

Author : Coke
Date   : 2025-05-13
"""

import logging
from datetime import timedelta
from typing import Any, overload

from redis.asyncio import Redis
from redis.typing import EncodableT, KeyT

logger = logging.getLogger(__name__)


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

    @staticmethod
    def _to_str(key: KeyT) -> str:
        """
        Converts the input `key` (of type memoryview, bytes, or any other type)
        into a string representation.

        Args:
            key (KeyT): The input value, which can be of type memoryview, bytes, or other types.

        Returns:
            str: The string representation of the input key.
        """

        if isinstance(key, memoryview):
            return key.tobytes().decode("utf-8")
        if isinstance(key, bytes):
            return key.decode("utf-8")
        return str(key)

    def _get_log(self, key: KeyT, response: Any) -> None:
        """
        Log Redis key access and corresponding response for debugging.

        Args:
            key (KeyT): The Redis key that was accessed.
            response (Any): The value or data returned from Redis.
        """
        self.logger.info('Attempting to retrieve value for key: "%s" from Redis.', key)
        self.logger.debug('Successfully retrieved value for key "%s": %s', key, response)

    @overload
    async def set(
        self,
        key: str,
        value: EncodableT | dict | list,
        *,
        ttl: int | timedelta | None = None,
        is_transaction: bool = False,
    ) -> None: ...

    @overload
    async def set(
        self,
        key: KeyT,
        value: EncodableT,
        *,
        ttl: int | timedelta | None = None,
        is_transaction: bool = False,
    ) -> None: ...

    async def set(
        self,
        key: KeyT,
        value: EncodableT | dict | list,
        *,
        ttl: int | timedelta | None = None,
        is_transaction: bool = False,
    ) -> None:
        """
        Sets a key-value pair in Redis.

        Args:
            key (KeyT): The key to store in Redis.
            value (EncodableT | dict | list): The value to store for the key.
            ttl (int | timedelta | None, optional): The time-to-live for the key. Defaults to None.
            is_transaction (bool, optional): Whether to perform this operation as part of a transaction.
        """

        async with self.client.pipeline(transaction=is_transaction) as pipe:
            if isinstance(value, dict):
                await pipe.hset(self._to_str(key), mapping=value)  # type: ignore

            elif isinstance(value, list):
                await pipe.lpush(self._to_str(key), *value)  # type: ignore

            else:
                await pipe.set(key, value)

            if ttl is not None:
                await pipe.expire(key, ttl)

            await pipe.execute()

        self.logger.info(
            'Setting key: "%s" with value: %s in Redis.',
            key,
            value,
        )

    async def get(self, key: KeyT) -> str:
        """
        Retrieves the value for a given key from Redis.

        Args:
            key (KeyT): The key to retrieve from Redis.

        Returns:
            str: The value associated with the key.
        """

        response = await self.client.get(key)

        self._get_log(key, response)
        return response

    async def get_mapping(self, key: str) -> dict:
        """
        Retrieve all fields and values from a Redis hash stored at the given key.

        Args:
            key (KeyT): The key of the Redis hash.

        Returns:
            dict: A dictionary containing all field-value pairs in the hash.
        """
        response = await self.client.hgetall(key)  # type: ignore

        self._get_log(key, response)
        return response

    async def get_array(self, key: str, *, start: int = 0, end: int = -1) -> list:
        """
        Retrieve a range of elements from a Redis list stored at the given key.

        Args:
            key (str): The key of the Redis list.
            start (int, optional): The starting index. Defaults to 0.
            end (int, optional): The ending index. Defaults to -1 (end of list).

        Returns:
            list: A list of elements from the specified range in the Redis list.
        """
        response = await self.client.lrange(key, start=start, end=end)  # type: ignore

        self._get_log(key, response)
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
