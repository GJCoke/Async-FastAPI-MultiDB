"""
Auth file.

Description.

Author : Coke
Date   : 2025-03-11
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter

from src.core.mysql import SessionDep
from src.core.route import BaseRoute
from src.models.test import testCrud
from src.schemas.response import Response

router = APIRouter(tags=["auth"], route_class=BaseRoute)


@router.post("/login/{user_id}")
async def login(session: SessionDep) -> Response[Any]:
    crud = testCrud
    test = await crud.get_paginate(session, size=2, order_by=crud.Model.id)

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
