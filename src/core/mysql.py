"""
MySQL Database Configuration.

This file configures the MySQL database connection using SQLAlchemy
and integrates it with FastAPI for asynchronous database operations.

Author : Coke
Date   : 2025-03-17
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings

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
async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


# Type alias for the database session dependency.
# def login(session: SessionDep):
SessionDep = Annotated[AsyncSession, Depends(get_db)]
