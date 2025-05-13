"""
Async redis client testcase.

Author : Coke
Date   : 2025-05-13
"""

import random

import pytest
import pytest_asyncio
from redis.asyncio import Redis

from src.core.redis_client import AsyncRedisClient
from tests.utils import random_lowercase, random_uppercase


@pytest_asyncio.fixture
async def redis_client(redis: Redis) -> AsyncRedisClient:
    await redis.flushall()
    return AsyncRedisClient(redis)


@pytest.mark.asyncio
async def test_redis_key_bytes(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase().encode("utf-8")
    random_value = random_uppercase()
    await redis_client.set(random_key, random_value)
    assert await redis_client.get(random_key) == random_value


@pytest.mark.asyncio
async def test_redis_key_memoryview(redis_client: AsyncRedisClient) -> None:
    random_key = memoryview(random_lowercase().encode("utf-8"))
    random_value = random_uppercase()
    await redis_client.set(random_key, random_value)
    assert await redis_client.get(random_key) == random_value


@pytest.mark.asyncio
async def test_redis_set_str(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_value = random_uppercase()
    await redis_client.set(random_key, random_value)
    assert await redis_client.get(random_key) == random_value


@pytest.mark.asyncio
async def test_redis_set_int(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_int = random.randint(1, 100)
    await redis_client.set(random_key, random_int)
    assert int(await redis_client.get(random_key)) == random_int


@pytest.mark.asyncio
async def test_redis_set_float(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_float = random.uniform(1.0, 10.0)
    await redis_client.set(random_key, random_float)
    assert float(await redis_client.get(random_key)) == random_float


@pytest.mark.asyncio
async def test_redis_set_bytes(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_bytes = random_uppercase().encode("utf-8")
    await redis_client.set(random_key, random_bytes)
    assert await redis_client.get(random_key) == random_bytes.decode("utf-8")


@pytest.mark.asyncio
async def test_redis_set_memoryview(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_memoryview = memoryview(random_uppercase().encode("utf-8"))
    await redis_client.set(random_key, random_memoryview)
    assert await redis_client.get(random_key) == random_memoryview.tobytes().decode("utf-8")


@pytest.mark.asyncio
async def test_redis_set_list(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_list = [random_lowercase(), random_uppercase()]
    await redis_client.set(random_key, random_list)
    assert set(await redis_client.get_array(random_key)) == set(random_list)
    assert len(await redis_client.get_array(random_key, end=0)) == 1
    assert len(await redis_client.get_array(random_key, start=2)) == 0


@pytest.mark.asyncio
async def test_redis_set_dict(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_map = {random_lowercase(): random_uppercase(), random_uppercase(): random_lowercase()}
    await redis_client.set(random_key, random_map)
    assert await redis_client.get_mapping(random_key) == random_map


@pytest.mark.asyncio
async def test_redis_exists_single(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_value = random_uppercase()
    await redis_client.set(random_key, random_value)
    assert await redis_client.exists(random_key)


@pytest.mark.asyncio
async def test_redis_exists_multiple(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_value = random_uppercase()
    await redis_client.set(random_key, random_value)
    await redis_client.set(random_value, random_key)
    assert await redis_client.exists(random_key, random_value)


@pytest.mark.asyncio
async def test_redis_not_exists(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    assert not await redis_client.exists(random_key)


@pytest.mark.asyncio
async def test_redis_delete_existing(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    random_value = random_uppercase()
    await redis_client.set(random_key, random_value)
    assert await redis_client.delete(random_key)


@pytest.mark.asyncio
async def test_redis_delete_missing(redis_client: AsyncRedisClient) -> None:
    random_key = random_lowercase()
    assert not await redis_client.delete(random_key)
