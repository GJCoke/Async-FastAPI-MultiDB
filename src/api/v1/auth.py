"""
Auth file.

Description.

Author : Coke
Date   : 2025-03-11
"""

import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends

from src.core.config import auth_settings
from src.core.route import BaseRoute
from src.deps.auth import AuthorDep, OAuth2Form
from src.deps.environment import check_debug
from src.schemas.auth import JWTUser, OAuth2TokenResponse
from src.schemas.response import Response
from src.utils.constants import DAYS
from src.utils.security import create_token

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=BaseRoute)


@router.get("/keys/public")
async def get_public_key() -> Response[str]:
    """Obtain the public key for RSA encryption of password."""

    return Response(data=auth_settings.RSA_PUBLIC_KEY.get_secret_value())


@router.post("/login")
async def login() -> Response[str]:
    return Response(data="123")


@router.post("/login/swagger", include_in_schema=False, dependencies=[Depends(check_debug)])
async def login_swagger(form: OAuth2Form) -> OAuth2TokenResponse:
    token = create_token(
        JWTUser(sub=uuid.uuid4(), username=form.username),  # type: ignore
        timedelta(seconds=1 * DAYS),
        auth_settings.ACCESS_TOKEN_KEY,
        auth_settings.JWT_ALG,
    )
    return OAuth2TokenResponse(access_token=token, token_type="bearer")


@router.get("/user/info")
async def get_user_info(user: AuthorDep) -> Response[str]:
    return Response(data="123")


@router.post("/refresh")
async def refresh_token(user: AuthorDep) -> Response[str]:
    return Response(data="123")
