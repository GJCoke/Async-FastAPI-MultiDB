"""
Auth file.

Description.

Author : Coke
Date   : 2025-03-11
"""

from fastapi import APIRouter

from src.core.route import BaseRoute
from src.schemas.auth import AuthRequest
from src.schemas.response import PaginatedResponse, Response

router = APIRouter(tags=["auth"], route_class=BaseRoute)


@router.post("/login")
async def login(body: AuthRequest) -> Response[PaginatedResponse]:
    return Response(data=PaginatedResponse())
