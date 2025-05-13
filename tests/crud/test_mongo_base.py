"""
Author  : Coke
Date    : 2025-05-10
"""

from typing import AsyncIterator

import pytest
import pytest_asyncio
from beanie import SortDirection, init_beanie
from beanie.operators import In
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.exceptions import InvalidParameterError, NotFoundException
from src.crud.crud_beanie import BaseBeanieCRUD
from src.models.base import Document
from src.schemas import BaseRequest, BaseResponse
from tests.conftest import pytest_settings
from tests.utils import random_lowercase, random_object_id


class PyMongo(Document):
    name: str

    class Settings:
        name = "py_mongo"


class PyMongoCreate(BaseRequest):
    name: str


class PyMongoUpdate(BaseRequest):
    name: str


class PyMongoResponse(BaseResponse):
    name: str


class CRUD(BaseBeanieCRUD[PyMongo, PyMongoCreate, PyMongoUpdate]):
    """Beanie Base CRUD."""


@pytest_asyncio.fixture(autouse=True)
async def mongo() -> AsyncIterator[None]:
    client: AsyncIOMotorClient = AsyncIOMotorClient(str(pytest_settings.MONGO_DATABASE_URL))
    await init_beanie(database=client["beanie_db"], document_models=[PyMongo])
    await PyMongo.delete_all()

    yield

    client.close()


@pytest_asyncio.fixture()
async def with_data() -> list[PyMongo]:
    items = [
        PyMongo(name="Item 1"),
        PyMongo(name="Item 2"),
        PyMongo(name="Item 3"),
    ]
    await PyMongo.insert_many(items)

    items = await PyMongo.find().to_list()
    return items


@pytest_asyncio.fixture
async def crud() -> CRUD:
    return CRUD(PyMongo)


@pytest.mark.asyncio
async def test_create_by_dict(crud: CRUD) -> None:
    name = random_lowercase()
    case = await crud.create({"name": name})
    assert case.name == name


@pytest.mark.asyncio
async def test_create_by_schema(crud: CRUD) -> None:
    name = random_lowercase()
    case = await crud.create(PyMongoCreate(name=name))
    assert case.name == name


@pytest.mark.asyncio
async def test_create_by_model(crud: CRUD) -> None:
    name = random_lowercase()
    case = await crud.create(PyMongo(name=name))
    assert case.name == name


@pytest.mark.asyncio
async def test_create_all_by_model(crud: CRUD) -> None:
    name = random_lowercase()
    name2 = random_lowercase()
    await crud.create_all([PyMongo(name=name), PyMongo(name=name2)])
    created = await crud.get_all(In(PyMongo.name, [name, name2]))
    assert len(created) == 2
    names = [item.name for item in created]
    assert name in names
    assert name2 in names


@pytest.mark.asyncio
async def test_create_all_by_empty(crud: CRUD) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.create_all([])


@pytest.mark.asyncio
async def test_create_all_by_schema(crud: CRUD) -> None:
    name = random_lowercase()
    name2 = random_lowercase()
    await crud.create_all([PyMongoCreate(name=name), PyMongoCreate(name=name2)])
    created = await crud.get_all(In(PyMongo.name, [name, name2]))
    assert len(created) == 2
    names = [item.name for item in created]
    assert name in names
    assert name2 in names


@pytest.mark.asyncio
async def test_create_all_by_dict(crud: CRUD) -> None:
    name = random_lowercase()
    name2 = random_lowercase()
    await crud.create_all([{"name": name}, {"name": name2}])
    created = await crud.get_all(In(PyMongo.name, [name, name2]))
    assert len(created) == 2
    names = [item.name for item in created]
    assert name in names
    assert name2 in names


@pytest.mark.asyncio
async def test_get_all_matches_fixture(crud: CRUD, with_data: list[PyMongo]) -> None:
    case = await crud.get_all()
    assert len(case) == len(with_data)
    assert isinstance(case[0], PyMongo)


@pytest.mark.asyncio
async def test_get_all_filter_by_name(crud: CRUD, with_data: list[PyMongo]) -> None:
    case = await crud.get_all(PyMongo.name == with_data[0].name)
    assert len(case) == 1
    assert case[0].name == with_data[0].name


@pytest.mark.asyncio
async def test_get_all_filter_no_match(crud: CRUD, with_data: list[PyMongo]) -> None:
    case = await crud.get_all(PyMongo.name == random_lowercase())
    assert len(case) == 0


@pytest.mark.asyncio
async def test_get_all_with_serializer(crud: CRUD, with_data: list[PyMongo]) -> None:
    case = await crud.get_all(serializer=PyMongoResponse)
    assert isinstance(case[0], PyMongoResponse)


@pytest.mark.asyncio
async def test_get_all_order_by_desc(crud: CRUD, with_data: list[PyMongo]) -> None:
    case = await crud.get_all(order_by=("id", SortDirection.DESCENDING))
    assert case[0] == with_data[-1]


@pytest.mark.asyncio
async def test_get_count_all(crud: CRUD, with_data: list[PyMongo]) -> None:
    count = await crud.get_count()
    assert count == len(with_data)


@pytest.mark.asyncio
async def test_get_count_filtered_match(crud: CRUD, with_data: list[PyMongo]) -> None:
    count = await crud.get_count(PyMongo.id == with_data[0].id)
    assert count == 1


@pytest.mark.asyncio
async def test_get_count_filtered_no_match(crud: CRUD) -> None:
    count = await crud.get_count(PyMongo.name == random_lowercase())
    assert count == 0


@pytest.mark.asyncio
async def test_get_nonexistent_id_returns_none(crud: CRUD) -> None:
    result = await crud.get(random_object_id())
    assert result is None


@pytest.mark.asyncio
async def test_get_nonexistent_id_raise(crud: CRUD) -> None:
    with pytest.raises(NotFoundException) as exc:
        await crud.get(random_object_id(), nullable=False)
    assert "not found" in str(exc.value)


@pytest.mark.asyncio
async def test_get_by_valid_id(crud: CRUD, with_data: list[PyMongo]) -> None:
    result = await crud.get(with_data[0].id, nullable=False)
    assert result == with_data[0]


@pytest.mark.asyncio
async def test_get_by_empty(crud: CRUD, with_data: list[PyMongo]) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.get(None, nullable=False)


@pytest.mark.asyncio
async def test_get_by_ids_partial_match(crud: CRUD, with_data: list[PyMongo]) -> None:
    result = await crud.get_by_ids([with_data[0].id, random_object_id()])
    assert len(result) == 1
    assert result[0] == with_data[0]


@pytest.mark.asyncio
async def test_get_by_ids_none_match(crud: CRUD) -> None:
    result = await crud.get_by_ids([random_object_id()])
    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_by_ids_empty(crud: CRUD) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.get_by_ids([])


@pytest.mark.asyncio
async def test_get_by_ids_with_serializer(crud: CRUD, with_data: list[PyMongo]) -> None:
    result = await crud.get_by_ids([with_data[0].id], serializer=PyMongoResponse)
    assert isinstance(result[0], PyMongoResponse)


@pytest.mark.asyncio
async def test_get_by_ids_ordered(crud: CRUD, with_data: list[PyMongo]) -> None:
    result = await crud.get_by_ids([with_data[0].id, with_data[1].id], order_by=("id", SortDirection.DESCENDING))
    assert result[0] == with_data[1]


@pytest.mark.asyncio
async def test_paginate_default(crud: CRUD, with_data: list[PyMongo]) -> None:
    page = await crud.get_paginate()
    assert page.total == len(with_data)
    assert page.records[0] == with_data[0]


@pytest.mark.asyncio
async def test_paginate_ordered_desc(crud: CRUD, with_data: list[PyMongo]) -> None:
    page = await crud.get_paginate(order_by=("id", SortDirection.DESCENDING))
    assert page.records[0] == with_data[-1]


@pytest.mark.asyncio
async def test_paginate_overflow_page(crud: CRUD, with_data: list[PyMongo]) -> None:
    page = await crud.get_paginate(page=len(with_data) + 1)
    assert len(page.records) == 0


@pytest.mark.asyncio
async def test_paginate_limited_size(crud: CRUD, with_data: list[PyMongo]) -> None:
    page = await crud.get_paginate(size=1)
    assert len(page.records) == 1


@pytest.mark.asyncio
async def test_paginate_with_serializer(crud: CRUD, with_data: list[PyMongo]) -> None:
    page = await crud.get_paginate(serializer=PyMongoResponse)
    assert page.total == len(with_data)
    assert isinstance(page.records[0], PyMongoResponse)


@pytest.mark.asyncio
async def test_update_with_dict(crud: CRUD, with_data: list[PyMongo]) -> None:
    name = random_lowercase()
    update_time = with_data[0].update_time
    update = await crud.update(with_data[0], {"name": name})
    assert update.name == name
    assert update.id == with_data[0].id
    assert with_data[0].update_time != update_time


@pytest.mark.asyncio
async def test_update_with_schema_model(crud: CRUD, with_data: list[PyMongo]) -> None:
    name = random_lowercase()
    update = await crud.update(with_data[0], PyMongoUpdate(name=name))
    assert update.name == name
    assert update.id == with_data[0].id


@pytest.mark.asyncio
async def test_update_with_full_model_instance(crud: CRUD, with_data: list[PyMongo]) -> None:
    name = random_lowercase()
    update_model = with_data[0]
    update_model.name = name
    update = await crud.update(with_data[0], update_model)
    assert update.name == name
    assert update.id == with_data[0].id


@pytest.mark.asyncio
async def test_update_invalid_field_raises_value_error(crud: CRUD, with_data: list[PyMongo]) -> None:
    with pytest.raises(ValueError):
        await crud.update(with_data[0], {"name_test": None})


@pytest.mark.asyncio
async def test_update_by_id_with_dict(crud: CRUD, with_data: list[PyMongo]) -> None:
    name = random_lowercase()
    update = await crud.update_by_id(with_data[0].id, {"name": name})
    assert update.name == name
    assert update.id == with_data[0].id


@pytest.mark.asyncio
async def test_update_by_empty(crud: CRUD, with_data: list[PyMongo]) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.update_by_id(None, {"name": "name"})


@pytest.mark.asyncio
async def test_update_by_id_with_schema(crud: CRUD, with_data: list[PyMongo]) -> None:
    name = random_lowercase()
    update = await crud.update_by_id(with_data[0].id, PyMongoUpdate(name=name))
    assert update.name == name
    assert update.id == with_data[0].id


@pytest.mark.asyncio
async def test_update_by_id_invalid_field_raises_value_error(crud: CRUD, with_data: list[PyMongo]) -> None:
    with pytest.raises(ValueError):
        await crud.update_by_id(with_data[0].id, {"name_test": None})


@pytest.mark.asyncio
async def test_update_all_multiple_documents(crud: CRUD, with_data: list[PyMongo]) -> None:
    name = random_lowercase()
    name2 = random_lowercase()
    await crud.update_all([{"name": name, "id": with_data[0].id}, {"name": name2, "id": with_data[1].id}])
    update = await crud.get_by_ids([with_data[0].id, with_data[1].id])
    assert update[0].name == name
    assert update[1].name == name2


@pytest.mark.asyncio
async def test_update_all_empty(crud: CRUD, with_data: list[PyMongo]) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.update_all([])


@pytest.mark.asyncio
async def test_update_all_missing_id_raises_value_error(crud: CRUD) -> None:
    with pytest.raises(ValueError):
        await crud.update_all([{"name": "no_id"}])


@pytest.mark.asyncio
async def test_delete_and_not_found_check(crud: CRUD, with_data: list[PyMongo]) -> None:
    deleted = await crud.delete(with_data[0].id)
    assert deleted.id == with_data[0].id
    assert deleted.name == with_data[0].name
    with pytest.raises(NotFoundException):
        await crud.get(with_data[0].id, nullable=False)


@pytest.mark.asyncio
async def test_delete_non_existent_id_raises_not_found(crud: CRUD) -> None:
    with pytest.raises(NotFoundException):
        await crud.delete(random_object_id())


@pytest.mark.asyncio
async def test_delete_id_empty(crud: CRUD) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.delete(None)


@pytest.mark.asyncio
async def test_delete_all_partial_and_full(crud: CRUD, with_data: list[PyMongo]) -> None:
    await crud.delete_all([with_data[0].id, with_data[1].id])
    remaining = await crud.get_all()
    assert len(remaining) == 1


@pytest.mark.asyncio
async def test_delete_all_with_non_existent_id(crud: CRUD, with_data: list[PyMongo]) -> None:
    await crud.delete_all([with_data[0].id, random_object_id()])
    remaining = await crud.get_all()
    assert len(remaining) == 2


@pytest.mark.asyncio
async def test_delete_all_empty(crud: CRUD) -> None:
    with pytest.raises(InvalidParameterError):
        await crud.delete_all([])
