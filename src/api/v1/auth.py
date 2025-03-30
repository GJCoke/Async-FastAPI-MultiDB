"""
Auth file.

Description.

Author : Coke
Date   : 2025-03-11
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter
from beanie import PydanticObjectId

from src.core.route import BaseRoute
from src.deps.database import MongoTestDep, SessionDep
from src.models.test import testCrud
from src.schemas.response import Response

router = APIRouter(tags=["auth"], route_class=BaseRoute)


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
    test1 = await mongo.get(PydanticObjectId("67e949583be5692177c22766"), nullable=False)
    # test = await mongo.get_all()
    print(test1, "12312312321321")
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
