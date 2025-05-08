"""
Fixtures for testing FastAPI application.

This module contains pytest fixtures used for testing a FastAPI application.

Author : Coke
Date   : 2025-05-07
"""

from typing import Any, AsyncIterator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

MYSQL_URL = "sqlite+aiosqlite://"
engine = create_async_engine(
    MYSQL_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    """
    Loads environment variables from the .env file.

    This fixture is automatically executed at the start of the test session
    to ensure that environment variables are loaded before any tests are run.
    """
    load_dotenv()


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """
    Provides an asynchronous database session for the test.

    This fixture sets up a session for interacting with the database and yields
    it to tests. The session will be committed to the database at the end of the test.

    Yields:
        AsyncSession: An asynchronous database session for performing queries.
    """
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def init(session: AsyncSession) -> None:
    """
    Initializes the database by filling it with test data.

    This fixture is responsible for preparing the database by running necessary
    initialization routines like adding required records or setting up the database
    schema.

    Args:
        session (AsyncSession): The database session to perform initialization.
    """
    from src.initdb import init_db

    await init_db(session)


@pytest_asyncio.fixture
async def client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncClient]:
    """
    Provides an asynchronous HTTP client for making requests to the FastAPI app.

    This fixture creates and returns a client that can be used to make HTTP requests
    to the FastAPI app. It also mocks database and permission checks for testing purposes.

    Args:
        monkeypatch (pytest.MonkeyPatch): The monkeypatch fixture for modifying dependencies.

    Yields:
        AsyncClient: The client to send requests to the FastAPI application.
    """
    from src.core import database, lifecycle
    from src.core.config import settings
    from src.deps.role import verify_user_permission
    from src.main import app

    monkeypatch.setattr(database, "ASYNC_DATABASE_URL", MYSQL_URL)

    async def async_none(*_args: Any, **_kwargs: Any) -> None:
        return None

    monkeypatch.setattr(lifecycle, "store_router_in_db", async_none)

    app.dependency_overrides[verify_user_permission] = lambda: None

    async with LifespanManager(app) as manager:
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url=f"https://{settings.API_PREFIX_V1}") as client:
            yield client
