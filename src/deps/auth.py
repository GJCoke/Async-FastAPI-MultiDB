"""
Auth Deps.

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
from src.crud.auth import UserCRUD
from src.deps.database import SessionDep
from src.models.auth import User
from src.schemas.auth import UserJWT
from src.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX_V1}/auth/login/swagger", auto_error=False)


def parse_jwt_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserJWT:
    """
    Parse the JWT access token and return the decoded user object.

    Args:
        token (str): The JWT access token passed via request header.

    Returns:
        UserJWT: The decoded user information extracted from the token.

    Raises:
        UnauthorizedException: If the token is invalid or decoding fails.
    """

    if token is None:
        raise UnauthorizedException()

    user = decode_token(token, auth_settings.ACCESS_TOKEN_KEY)

    if not user:
        raise UnauthorizedException()

    return user


UserJWTDep = Annotated[UserJWT, Depends(parse_jwt_user)]

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_auth_crud(session: SessionDep) -> UserCRUD:
    """
    Provides an instance of UserCRUD for authentication logic.

    Args:
        session (SessionDep): The database session injected from request context.

    Returns:
        UserCRUD: An initialized CRUD instance for user operations.
    """
    return UserCRUD(User, session=session)


AuthCrudDep = Annotated[UserCRUD, Depends(get_auth_crud)]


async def get_current_user_form_db(user: UserJWTDep, db_user: AuthCrudDep) -> User:
    """
    Retrieve the full user information from the database based on the user ID extracted from the JWT token.

    Args:
        user (UserJWTDep): The JWT payload containing the user_id, extracted via token parsing.
        db_user (AuthCrudDep): The CRUD class for user operations, injected as a dependency.

    Returns:
        User: The full user model fetched from the database.

    Raises:
        UnauthorizedException: If the token is invalid or decoding fails.
        NotFoundException: If no user is found in the database with the given ID.
    """
    user_info = await db_user.get(user.user_id, nullable=False)
    return user_info


UserDBDep = Annotated[User, Depends(get_current_user_form_db)]
