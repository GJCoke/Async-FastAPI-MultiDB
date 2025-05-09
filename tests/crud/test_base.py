"""
test_base file.

Description.

Author : Coke
Date   : 2025-05-08
"""

import pytest
import pytest_asyncio
from sqlmodel import SQLModel as _SQLModel
from sqlmodel import col, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import NotFoundException
from src.crud.base import BaseSQLModelCRUD
from src.models.base import SQLModel
from src.schemas import BaseRequest, BaseResponse
from tests.conftest import engine
from tests.utils import random_lowercase, random_uuid


class PyUser(SQLModel, table=True):
    __tablename__ = "test"
    name: str


class PyUserCreate(BaseRequest):
    name: str


class PyUserUpdate(BaseRequest):
    name: str


class PyUserResponse(BaseResponse):
    name: str


class CRUD(BaseSQLModelCRUD[PyUser, PyUserCreate, PyUserUpdate]):
    """Base CRUD."""


@pytest_asyncio.fixture
async def crud(session: AsyncSession) -> CRUD:
    async with engine.begin() as connection:
        await connection.run_sync(_SQLModel.metadata.create_all)

    return CRUD(PyUser, session=session)


@pytest_asyncio.fixture
async def with_data(session: AsyncSession) -> list[PyUser]:
    await session.exec(delete(PyUser))  # type: ignore
    await session.commit()

    items = [
        PyUser(name="Item 1"),
        PyUser(name="Item 2"),
        PyUser(name="Item 3"),
    ]
    session.add_all(items)
    await session.commit()

    return items


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


@pytest.mark.asyncio
async def test_get_all_returns_all_users(crud: CRUD, with_data: list[PyUser]) -> None:
    case = await crud.get_all()
    assert len(case) == len(with_data)
    assert isinstance(case[0], PyUser)


@pytest.mark.asyncio
async def test_get_all_with_filter_returns_matching_user(crud: CRUD, with_data: list[PyUser]) -> None:
    case = await crud.get_all(col(PyUser.name) == with_data[0].name)
    assert len(case) == 1
    assert case[0].name == with_data[0].name


@pytest.mark.asyncio
async def test_get_all_with_invalid_filter_returns_empty(crud: CRUD) -> None:
    case = await crud.get_all(col(PyUser.name) == random_lowercase())
    assert len(case) == 0


@pytest.mark.asyncio
async def test_get_all_with_serializer(crud: CRUD) -> None:
    case = await crud.get_all(serializer=PyUserResponse)
    assert isinstance(case[0], PyUserResponse)


@pytest.mark.asyncio
async def test_get_all_with_order(crud: CRUD, with_data: list[PyUser]) -> None:
    case = await crud.get_all(order_by=col(PyUser.id).desc())
    assert case[0] == with_data[-1]


@pytest.mark.asyncio
async def test_get_count(crud: CRUD, with_data: list[PyUser]) -> None:
    count = await crud.get_count()
    assert count == len(with_data)


@pytest.mark.asyncio
async def test_get_count_with_filter(crud: CRUD, with_data: list[PyUser]) -> None:
    count = await crud.get_count(col(PyUser.name) == with_data[0].name)
    assert count == 1


@pytest.mark.asyncio
async def test_get_count_with_invalid_filter(crud: CRUD) -> None:
    count = await crud.get_count(col(PyUser.name) == random_lowercase())
    assert count == 0


@pytest.mark.asyncio
async def test_get_by_invalid_id_returns_none(crud: CRUD) -> None:
    result = await crud.get(random_uuid())
    assert result is None


@pytest.mark.asyncio
async def test_get_by_invalid_id_with_nullable_false_raises(crud: CRUD) -> None:
    with pytest.raises(NotFoundException) as exc:
        await crud.get(random_uuid(), nullable=False)
    assert "not found" in str(exc.value)


@pytest.mark.asyncio
async def test_get_by_id_success(crud: CRUD, with_data: list[PyUser]) -> None:
    result = await crud.get(with_data[0].id)
    assert result == with_data[0]


@pytest.mark.asyncio
async def test_get_by_ids_mixed(crud: CRUD, with_data: list[PyUser]) -> None:
    result = await crud.get_by_ids([with_data[0].id, random_uuid()])
    assert len(result) == 1
    assert result[0] == with_data[0]


@pytest.mark.asyncio
async def test_get_by_ids_all_invalid(crud: CRUD) -> None:
    result = await crud.get_by_ids([random_uuid()])
    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_by_ids_empty_list(crud: CRUD) -> None:
    result = await crud.get_by_ids([])
    assert result == []


@pytest.mark.asyncio
async def test_get_by_ids_with_serializer(crud: CRUD, with_data: list[PyUser]) -> None:
    result = await crud.get_by_ids([with_data[0].id], serializer=PyUserResponse)
    assert isinstance(result[0], PyUserResponse)


@pytest.mark.asyncio
async def test_get_by_ids_with_order(crud: CRUD, with_data: list[PyUser]) -> None:
    result = await crud.get_by_ids([with_data[0].id, with_data[1].id], order_by=col(PyUser.id).desc())
    assert result[0] == with_data[1]


@pytest.mark.asyncio
async def test_get_paginate_default(crud: CRUD, with_data: list[PyUser]) -> None:
    page = await crud.get_paginate()
    assert page.total == len(with_data)
    assert page.records[0] == with_data[0]


@pytest.mark.asyncio
async def test_get_paginate_desc_order(crud: CRUD, with_data: list[PyUser]) -> None:
    page = await crud.get_paginate(order_by=col(PyUser.id).desc())
    assert page.records[0] == with_data[-1]


@pytest.mark.asyncio
async def test_get_paginate_out_of_range_page_returns_empty(crud: CRUD, with_data: list[PyUser]) -> None:
    page = await crud.get_paginate(page=len(with_data) + 1)
    assert len(page.records) == 0


@pytest.mark.asyncio
async def test_get_paginate_size_zero_returns_empty(crud: CRUD, with_data: list[PyUser]) -> None:
    page = await crud.get_paginate(size=0)
    assert page.total == len(with_data)
    assert len(page.records) == 0


@pytest.mark.asyncio
async def test_get_paginate_size_one_returns_single(crud: CRUD) -> None:
    page = await crud.get_paginate(size=1)
    assert len(page.records) == 1


@pytest.mark.asyncio
async def test_get_paginate_with_serializer(crud: CRUD, with_data: list[PyUser]) -> None:
    page = await crud.get_paginate(serializer=PyUserResponse)
    assert page.total == len(with_data)
    assert isinstance(page.records[0], PyUserResponse)
