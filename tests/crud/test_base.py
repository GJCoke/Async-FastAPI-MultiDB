"""
test_base file.

Description.

Author : Coke
Date   : 2025-05-08
"""

import pytest
import pytest_asyncio
from sqlmodel import SQLModel as _SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.base import BaseSQLModelCRUD
from src.models.base import SQLModel
from src.schemas import BaseModel
from tests.conftest import engine


class PyUser(SQLModel, table=True):
    __tablename__ = "test"
    name: str


class PyUserCreate(BaseModel):
    name: str


class PyUserUpdate(BaseModel):
    name: str


class CRUD(BaseSQLModelCRUD[PyUser, PyUserCreate, PyUserUpdate]):
    """Base CRUD."""


@pytest_asyncio.fixture
async def crud(session: AsyncSession) -> CRUD:
    async with engine.begin() as connection:
        await connection.run_sync(_SQLModel.metadata.create_all)

    return CRUD(PyUser, session=session)


@pytest.mark.asyncio
async def test_create_with_dict(crud: CRUD) -> None:
    case = await crud.create({"name": "case"})
    assert case.name == "case"


@pytest.mark.asyncio
async def test_create_with_schema(crud: CRUD) -> None:
    case = await crud.create(PyUserCreate(name="case1"))
    assert case.name == "case1"


@pytest.mark.asyncio
async def test_create_with_model(crud: CRUD) -> None:
    case = await crud.create(PyUser(name="case2"))
    assert case.name == "case2"


@pytest.mark.asyncio
async def test_create_invalid_dict_without_validation(crud: CRUD) -> None:
    with pytest.raises(TypeError) as exc:
        await crud.create({"name": "case3"}, validate=False)
    assert "Expected type" in str(exc.value)


@pytest.mark.asyncio
async def test_create_invalid_schema_without_validation(crud: CRUD) -> None:
    with pytest.raises(TypeError) as exc:
        await crud.create(PyUserCreate(name="case4"), validate=False)
    assert "Expected type" in str(exc.value)
