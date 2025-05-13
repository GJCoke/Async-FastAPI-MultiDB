"""
test_base file.

Description.

Author : Coke
Date   : 2025-05-08
"""

import pytest
import pytest_asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Field, col, delete
from sqlmodel import SQLModel as _SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import ExistsException, InvalidParameterError, NotFoundException
from src.crud.base import BaseSQLModelCRUD
from src.models.base import SQLModel
from src.schemas import BaseRequest, BaseResponse
from tests.conftest import engine
from tests.utils import random_lowercase, random_uuid


class PyUser(SQLModel, table=True):
    __tablename__ = "test"
    name: str = Field(..., unique=True)


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
    name = random_lowercase()
    case = await crud.create({"name": name})
    assert case.name == name


@pytest.mark.asyncio
async def test_create_with_schema(crud: CRUD) -> None:
    name = random_lowercase()
    case = await crud.create(PyUserCreate(name=name))
    assert case.name == name


@pytest.mark.asyncio
async def test_create_with_model(crud: CRUD) -> None:
    name = random_lowercase()
    case = await crud.create(PyUser(name=name))
    assert case.name == name


@pytest.mark.asyncio
async def test_create_with_schema_not_validate(crud: CRUD) -> None:
    name = random_lowercase()
    with pytest.raises(InvalidParameterError) as exc:
        await crud.create(PyUserCreate(name=name), validate=False)  # type: ignore
    assert "Expected type" in str(exc.value)


@pytest.mark.asyncio
async def test_create_repeat_creation(crud: CRUD) -> None:
    name = random_lowercase()
    await crud.create(PyUser(name=name))
    with pytest.raises(ExistsException):
        await crud.create(PyUser(name=name))


@pytest.mark.asyncio
async def test_create_all_schema(crud: CRUD) -> None:
    name = random_lowercase()
    name2 = random_lowercase()
    await crud.create_all([PyUserCreate(name=name), PyUserCreate(name=name2)])

    created = await crud.get_all(col(PyUser.name).in_([name, name2]))
    assert len(created) == 2
    names = [item.name for item in created]
    assert name in names
    assert name2 in names


@pytest.mark.asyncio
async def test_create_all_dict(crud: CRUD) -> None:
    name = random_lowercase()
    name2 = random_lowercase()
    await crud.create_all([{"name": name}, {"name": name2}])

    created = await crud.get_all(col(PyUser.name).in_([name, name2]))
    assert len(created) == 2
    names = [item.name for item in created]
    assert name in names
    assert name2 in names


@pytest.mark.asyncio
async def test_create_all_model(crud: CRUD) -> None:
    name = random_lowercase()
    name2 = random_lowercase()
    await crud.create_all([PyUser(name=name), PyUser(name=name2)])

    created = await crud.get_all(col(PyUser.name).in_([name, name2]))
    assert len(created) == 2
    names = [item.name for item in created]
    assert name in names
    assert name2 in names


@pytest.mark.asyncio
async def test_create_all_empty(crud: CRUD) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.create_all([])


@pytest.mark.asyncio
async def test_create_all_repeat(crud: CRUD) -> None:
    name = random_lowercase()
    with pytest.raises(ExistsException):
        await crud.create_all([PyUser(name=name), PyUser(name=name)])


@pytest.mark.asyncio
async def test_crud_session(crud: CRUD) -> None:
    crud._session = None
    with pytest.raises(RuntimeError):
        await crud.get_all()


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
    result = await crud.get(with_data[0].id, nullable=False)
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
    with pytest.raises(InvalidParameterError):
        await crud.get_by_ids([])


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


@pytest.mark.asyncio
async def test_update_with_dict(crud: CRUD, with_data: list[PyUser]) -> None:
    name = random_lowercase()
    update = await crud.update(with_data[0], {"name": name})
    assert update.name == name
    assert update.id == with_data[0].id


@pytest.mark.asyncio
async def test_update_with_schema(crud: CRUD, with_data: list[PyUser]) -> None:
    name = random_lowercase()
    update = await crud.update(with_data[0], PyUserUpdate(name=name))
    assert update.name == name
    assert update.id == with_data[0].id


@pytest.mark.asyncio
async def test_update_with_model_instance(crud: CRUD, with_data: list[PyUser]) -> None:
    name = random_lowercase()
    update_model = with_data[0]
    update_model.name = name
    update = await crud.update(with_data[0], update_model)
    assert update.name == name
    assert update.id == with_data[0].id


@pytest.mark.asyncio
async def test_update_invalid_field_raises(crud: CRUD, with_data: list[PyUser]) -> None:
    with pytest.raises(ValueError):
        await crud.update(with_data[0], {"name_test": None})


@pytest.mark.asyncio
async def test_update_by_id_with_dict(crud: CRUD, with_data: list[PyUser]) -> None:
    name = random_lowercase()
    update = await crud.update_by_id(with_data[0].id, {"name": name})
    assert update.name == name
    assert update.id == with_data[0].id


@pytest.mark.asyncio
async def test_update_by_id_with_schema(crud: CRUD, with_data: list[PyUser]) -> None:
    name = random_lowercase()
    update = await crud.update_by_id(with_data[0].id, PyUserUpdate(name=name))
    assert update.name == name
    assert update.id == with_data[0].id


@pytest.mark.asyncio
async def test_update_by_id_invalid_field_raises(crud: CRUD, with_data: list[PyUser]) -> None:
    with pytest.raises(ValueError):
        await crud.update_by_id(with_data[0].id, {"name_test": None})


@pytest.mark.asyncio
async def test_update_all_success(crud: CRUD, with_data: list[PyUser]) -> None:
    name = random_lowercase()
    name2 = random_lowercase()
    await crud.update_all([{"name": name, "id": with_data[0].id}, {"name": name2, "id": with_data[1].id}])
    update = await crud.get_by_ids([with_data[0].id, with_data[1].id])
    assert update[0].name == name
    assert update[1].name == name2


@pytest.mark.asyncio
async def test_update_all_missing_id_raises(crud: CRUD) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.update_all([{"name": "no_id"}])


@pytest.mark.asyncio
async def test_update_all_not_found_id_raises(crud: CRUD) -> None:
    with pytest.raises(NotFoundException):
        await crud.update_all([{"name": "test", "id": random_uuid()}])


@pytest.mark.asyncio
async def test_update_all_empty(crud: CRUD) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.update_all([])


@pytest.mark.asyncio
async def test_update_all_error(crud: CRUD, with_data: list[PyUser]) -> None:
    with pytest.raises(SQLAlchemyError):
        await crud.update_all([{"name1": "test", "id": with_data[0].id}])


@pytest.mark.asyncio
async def test_delete_single_success(crud: CRUD, with_data: list[PyUser]) -> None:
    deleted = await crud.delete(with_data[0].id)
    assert deleted.id == with_data[0].id
    assert deleted.name == with_data[0].name
    with pytest.raises(NotFoundException):
        await crud.get(with_data[0].id, nullable=False)


@pytest.mark.asyncio
async def test_delete_single_not_found_raises(crud: CRUD) -> None:
    with pytest.raises(NotFoundException):
        await crud.delete(random_uuid())


@pytest.mark.asyncio
async def test_delete_all_success(crud: CRUD, with_data: list[PyUser]) -> None:
    await crud.delete_all([with_data[0].id, with_data[1].id])
    remaining = await crud.get_all()
    assert len(remaining) == 1


@pytest.mark.asyncio
async def test_delete_all_partial_not_found(crud: CRUD, with_data: list[PyUser]) -> None:
    await crud.delete_all([with_data[0].id, random_uuid()])
    remaining = await crud.get_all()
    assert len(remaining) == 2


@pytest.mark.asyncio
async def test_delete_all_empty(crud: CRUD) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.delete_all([])
