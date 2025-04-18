"""
Auth JWT.

This module provides JWT-based user authentication utilities
for FastAPI routes, including token parsing and user injection.

Author : Coke
Date   : 2025-04-17
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.core.config import auth_settings, settings
from src.core.exceptions import UnauthorizedException
from src.schemas.auth import JWTUser
from src.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX_V1}/auth/login/swagger", auto_error=False)


def parse_jwt_user(token: Annotated[str, Depends(oauth2_scheme)]) -> JWTUser:
    """
    Parse the JWT access token and return the decoded user object.

    Args:
        token (str): The JWT access token passed via request header.

    Returns:
        JWTUser: The decoded user information extracted from the token.

    Raises:
        UnauthorizedException: If the token is invalid or decoding fails.
    """

    user = decode_token(token, auth_settings.ACCESS_TOKEN_KEY)

    if not user:
        raise UnauthorizedException()

    return user


AuthorDep = Annotated[JWTUser, Depends(parse_jwt_user)]

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
