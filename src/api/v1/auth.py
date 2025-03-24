"""
Auth file.

Description.

Author : Coke
Date   : 2025-03-11
"""

from fastapi import APIRouter, Query

from src.core.route import BaseRoute
from src.schemas.auth import AuthRequest
from src.schemas.response import PaginatedResponse, Response

router = APIRouter(tags=["auth"], route_class=BaseRoute)


@router.post("/login/{user_data}")
async def login(user_data: str, body: AuthRequest = Query()) -> Response[PaginatedResponse]:
    return Response(data=PaginatedResponse())
