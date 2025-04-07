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
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.route import BaseRoute
from src.deps.database import MongoTestDep, SessionDep, SQLTestDep
from src.models.test import Test as TestModel
from src.models.test import testCrud
from src.schemas.base import BaseModel
from src.schemas.response import Response

router = APIRouter(tags=["auth"], route_class=BaseRoute)


class Test(BaseModel):
    id: PydanticObjectId
    name: str
    desc_test: str


@router.post("/login/{user_id}")
async def login(mongo: MongoTestDep, name: str, crud: SQLTestDep) -> Response[Any]:
    # crud = testCrud

    # await redis.set("test", "vvvvvvvv")
    # await redis.get("cccc")
    # test = TestDocument(name="12345")
    # await test.insert()
    # test = await TestDocument.find_one(TestDocument.name == "12345")
    # test.desc_test = "running me111111!"
    # await test.save()
    # info = await TestDocument.find_all().to_list()
    # result = await redis.exists("test", "ccc")
    _sql = await crud.get_all()

    _mongo = await mongo.create({"name": name})
    # test1 = await mongo.get(PydanticObjectId("67e949583be5692177c22766"), nullable=False)
    # test = await mongo.get_all()
    # test_all = []
    # for item in test:
    #     test_all.append(Test.model_validate(item.model_dump()))

    # _id = PydanticObjectId("67ea02faad4c83746bc652d0")
    # print(_id, "asdasdsa")
    # test_all = await mongo.get_by_ids([_id])

    return Response(data={"mongo_a": settings.DATABASE_MONGO_URL, "sql": _sql, "mongo": _mongo})


@router.post("/add/test")
async def add_test(session1: SessionDep) -> Response[Any]:
    async def affiliation(session: AsyncSession) -> None:
        company_structure = dict(
            name="霸天集团",
            children=[
                dict(name="机械部队", children=[dict(name="机甲小队"), dict(name="机器人兵团"), dict(name="战车队")]),
                dict(name="战略部", children=[dict(name="情报分析组"), dict(name="指挥决策组")]),
                dict(name="科技部", children=[dict(name="高能武器组"), dict(name="人工智能组")]),
                dict(name="资源部", children=[dict(name="矿产采集组"), dict(name="能源管理组")]),
                dict(name="后勤部", children=[dict(name="物资供应组"), dict(name="人员调度组")]),
            ],
        )

        _corporation = TestModel(name=company_structure["name"])  # type: ignore
        session.add(_corporation)
        await session.commit()

        async def recursion(children: list) -> None:
            for item in children:
                _item = TestModel(name=item.get("name"))
                session.add(_item)
                await session.commit()

                if item.get("children"):
                    await recursion(item["children"])  # type: ignore

        await recursion(company_structure["children"])  # type: ignore

    await affiliation(session1)
    return Response(data=None)


@router.put("/add/test")
async def put_test(session: SessionDep, id: UUID, name: str) -> Response[Any]:
    crud = testCrud
    response = await crud.update_by_id(id, {"name": name, "desc_test": "desc1111"}, session=session)
    return Response(data=response)
