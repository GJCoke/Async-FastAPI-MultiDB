"""
Auth file.

Description.

Author : Coke
Date   : 2025-03-11
"""

from typing import Any
from uuid import UUID

from beanie import PydanticObjectId
from fastapi import APIRouter

from src.core.route import BaseRoute
from src.deps.database import MongoTestDep, SessionDep
from src.models.test import testCrud
from src.schemas.base import BaseModel
from src.schemas.response import Response

router = APIRouter(tags=["auth"], route_class=BaseRoute)


class Test(BaseModel):
    id: PydanticObjectId
    name: str
    desc_test: str


@router.post("/login/{user_id}")
async def login(mongo: MongoTestDep, name: str, session: SessionDep) -> Response[Any]:
    crud = testCrud

    # await redis.set("test", "vvvvvvvv")
    # await redis.get("cccc")
    # test = TestDocument(name="12345")
    # await test.insert()
    # test = await TestDocument.find_one(TestDocument.name == "12345")
    # test.desc_test = "running me111111!"
    # await test.save()
    # info = await TestDocument.find_all().to_list()
    # result = await redis.exists("test", "ccc")
    test = await crud.get(session, UUID("0195e257-d45a-71ad-9cdb-7065e0be4323"))

    # test = await mongo.create({"name": name})
    # test1 = await mongo.get(PydanticObjectId("67e949583be5692177c22766"), nullable=False)
    # test = await mongo.get_all()
    # test_all = []
    # for item in test:
    #     test_all.append(Test.model_validate(item.model_dump()))

    # _id = PydanticObjectId("67ea02faad4c83746bc652d0")
    # print(_id, "asdasdsa")
    # test_all = await mongo.get_by_ids([_id])

    return Response(data=test)


@router.post("/add/test")
async def add_test(session: SessionDep, name: str) -> Response[Any]:
    crud = testCrud
    response = await crud.create(session, {"name": name})
    return Response(data=response)


@router.put("/add/test")
async def put_test(session: SessionDep, id: UUID, name: str) -> Response[Any]:
    crud = testCrud
    response = await crud.update_by_id(session, id, {"name": name, "desc_test": "desc1111"})
    return Response(data=response)
