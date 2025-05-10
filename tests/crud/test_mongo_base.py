"""
Author  : Coke
Date    : 2025-05-10
"""

import pytest
import pytest_asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.models.base import Document
from tests.conftest import pytest_settings


class PyMongo(Document):
    name: str

    class Settings:
        name = "counter"


@pytest_asyncio.fixture(autouse=True)
async def mongo():
    client = AsyncIOMotorClient(str(pytest_settings.MONGO_DATABASE_URL))

    await init_beanie(database=client["beanie_db"], document_models=[PyMongo])

    yield

    client.close()


@pytest.mark.asyncio
async def test_mongo():
    add = PyMongo(name="add")
    await add.save()

    data = await PyMongo.find_all().to_list()
    print(data, "12321321321321")
