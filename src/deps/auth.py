"""
Auth Deps.

This module provides JWT-based user authentication utilities
for FastAPI routes, including token parsing and user injection.

Author : Coke
Date   : 2025-04-17
"""

import logging

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import Annotated, Doc

from src.core.config import auth_settings, settings
from src.core.exceptions import BadRequestException, PermissionDeniedException, UnauthorizedException
from src.crud.auth import UserCRUD
from src.deps.database import RedisDep, SessionDep
from src.deps.router import RequestRouterDep
from src.models.auth import User
from src.schemas.auth import UserAccessJWT, UserRefreshJWT
from src.utils.security import decode_token

__all__ = [
    "OAuth2Form",
    "HeaderRefreshTokenDep",
    "HeaderAccessTokenDep",
    "HeaderUserAgentDep",
    "UserRefreshDep",
    "UserRefreshJWTDep",
    "UserAccessJWTDep",
    "UserDBDep",
    "AuthCrudDep",
    "refresh_structure",
    "oauth2_scheme",
]

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX_V1}/auth/login/swagger", auto_error=False)
refresh_structure = "auth:refresh:<{user_id}>:<{jti}>"
permission_structure = "auth:permission:<{user_id}>"

OAuth2Form = Annotated[
    OAuth2PasswordRequestForm,
    Depends(),
    Doc(
        """
        OAuth2 password login form, containing the username and password fields.
        This is used to authenticate users via the OAuth2 password flow.
        """
    ),
]


def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """
    Dependency to extract and validate the access token from the Authorization header.

    Args:
        token (str): The JWT access token obtained from the request header.

    Raises:
        UnauthorizedException: If no token is provided or token is invalid.

    Returns:
        str: The extracted JWT access token.
    """
    if token is None:
        logger.debug("No token is provided.")
        raise UnauthorizedException()

    return token


def get_refresh_token(x_refresh_token: Annotated[str, Header(...)]) -> str:
    """
    Dependency to extract the refresh token from the 'x-refresh-token' request header.

    Args:
        x_refresh_token (str): The refresh token from the custom header.

    Raises:
        PermissionDeniedException: If the header is missing.

    Returns:
        str: The extracted refresh token.
    """
    if x_refresh_token is None:
        logger.debug("No refresh token is provided.")
        raise PermissionDeniedException()

    return x_refresh_token


def get_user_agent(user_agent: Annotated[str, Header(..., include_in_schema=False)]) -> str:
    """
    Dependency to extract the User-Agent from the request header.

    Args:
        user_agent (str): The User-Agent string from the header.

    Raises:
        BadRequestException: If the header is missing.

    Returns:
        str: The extracted User-Agent string.
    """
    if user_agent is None:
        logger.debug("No User-Agent is provided.")
        raise BadRequestException()

    return user_agent


HeaderRefreshTokenDep = Annotated[
    str,
    Depends(get_refresh_token),
    Doc(
        """
        A typed dependency to inject the refresh token from the request header.
        This token is used for refreshing JWT access tokens and handling session re-authentication.
        """
    ),
]

HeaderUserAgentDep = Annotated[
    str,
    Depends(get_user_agent),
    Doc(
        """
        A typed dependency to inject the User-Agent header from the request.
        This can be used to track the client's environment or for device-specific logic.
        """
    ),
]
HeaderAccessTokenDep = Annotated[
    str,
    Depends(get_access_token),
    Doc(
        """
        A typed dependency to inject the validated JWT access token from headers.
        Useful for route functions that require authentication.
        """
    ),
]


def parse_access_jwt_user(token: HeaderAccessTokenDep) -> UserAccessJWT:
    """
    Parse the JWT access token and return the decoded user object.

    Args:
        token (str): The JWT access token passed via request header.

    Returns:
        UserAccessJWT: The decoded user information extracted from the token.

    Raises:
        UnauthorizedException: If the token is invalid or decoding fails.
    """

    user = decode_token(token, auth_settings.ACCESS_TOKEN_KEY)

    return user


def parse_refresh_jwt_user(
    x_refresh_token: HeaderRefreshTokenDep,
    user_agent: HeaderUserAgentDep,
) -> UserRefreshJWT:
    """
    Parse the JWT refresh access token and return the decoded user object.

    Args:
        x_refresh_token (str): The JWT refresh access token passed via request header.
        user_agent (str): The user agent via request header.

    Returns:
        UserAccessJWT: The decoded user information extracted from the token.

    Raises:
        UnauthorizedException: If the token is invalid or decoding fails.
        BadRequestException: if the device information does not match.
    """

    user = decode_token(x_refresh_token, auth_settings.REFRESH_TOKEN_KEY)

    if user.agent != user_agent:
        logger.warning(
            "User-Agent mismatch detected: original request User-Agent '%s'"
            " does not match refresh token User-Agent '%s'.",
            user_agent,
            user.agent,
        )
        raise BadRequestException()

    return user


UserAccessJWTDep = Annotated[
    UserAccessJWT,
    Depends(parse_access_jwt_user),
    Doc(
        """
        Dependency that provides the decoded user information from the access JWT token.

        This dependency uses the `parse_access_jwt_user` function to decode the JWT access token passed
        via the request header, and injects the decoded user information (as a `UserAccessJWT` object) into
        the route. If the token is invalid or decoding fails, an `UnauthorizedException` will be raised.

        The decoded `UserAccessJWT` contains the user's identity and other relevant data extracted from the token.
        """
    ),
]
UserRefreshJWTDep = Annotated[
    UserRefreshJWT,
    Depends(parse_refresh_jwt_user),
    Doc(
        """
        Dependency that extracts and decodes the refresh JWT token from the request header.

        It ensures that the refresh token is valid, and the device making the request matches
        the one stored in the token. If the token is invalid or the device mismatch occurs,
        it raises a `PermissionDeniedException` or `BadRequestException`.

        This dependency is used to retrieve the user information stored in the refresh token,
        which is typically required for refreshing the access token or verifying the user's session.
        """
    ),
]


async def get_auth_crud(session: SessionDep) -> UserCRUD:
    """
    Provides an instance of UserCRUD for authentication logic.

    Args:
        session (SessionDep): The database session injected from request context.

    Returns:
        UserCRUD: An initialized CRUD instance for user operations.
    """
    return UserCRUD(User, session=session)


AuthCrudDep = Annotated[
    UserCRUD,
    Depends(get_auth_crud),
    Doc(
        """
        Dependency that provides an instance of `UserCRUD` for performing user authentication operations.
        This dependency uses the `get_auth_crud` function to inject a session-based `UserCRUD` instance
        into the route, allowing for operations like user retrieval and updates related to authentication.
        """
    ),
]


async def get_current_user_form_db(user: UserAccessJWTDep, db_user: AuthCrudDep) -> User:
    """
    Retrieve the full user information from the database based on the user ID extracted from the JWT token.

    Args:
        user (UserAccessJWTDep): The JWT payload containing the user_id, extracted via token parsing.
        db_user (AuthCrudDep): The CRUD class for user operations, injected as a dependency.

    Returns:
        User: The full user model fetched from the database.

    Raises:
        UnauthorizedException: If the token is invalid or decoding fails or no user is found in the database.
    """
    user_info = await db_user.get(user.user_id)
    if not user_info:
        logger.debug("No user found in the database.")
        raise UnauthorizedException()
    return user_info


async def get_current_user_form_redis_and_db(user: UserRefreshJWTDep, db_user: AuthCrudDep, redis: RedisDep) -> User:
    """
    Retrieves the current user from both Redis and the database.

    This function first checks if a valid refresh token is present in Redis.
    If the token is not found, or the user does not exist in the database,
    a `PermissionDeniedException` is raised.

    Args:
        user (UserRefreshJWTDep): The decoded user information from the refresh token.
        db_user (AuthCrudDep): The dependency to fetch user details from the database.
        redis (RedisDep): The dependency to interact with Redis to fetch the refresh token.

    Returns:
        User: The user object fetched from the database.

    Raises:
        PermissionDeniedException: If the refresh token is missing or the user is not found in the database.
    """
    refresh_token = redis.get(refresh_structure.format(user_id=user.user_id, jti=user.jti))

    if not refresh_token:
        logger.debug("No refresh token found in the redis.")
        raise PermissionDeniedException()

    user_info = await db_user.get(user.user_id)
    if not user_info:
        logger.debug("No user found in the database.")
        raise PermissionDeniedException()

    return user_info


UserDBDep = Annotated[
    User,
    Depends(get_current_user_form_db),
    Doc(
        """
        This dependency uses the `get_current_user_form_db` function to retrieve the user
        details from the database. It is intended for use in route functions where user data
        needs to be fetched directly from the database.
        """
    ),
]
UserRefreshDep = Annotated[
    User,
    Depends(get_current_user_form_redis_and_db),
    Doc(
        """
        This dependency first checks if the user's refresh token exists in Redis. If the token
        is found, it fetches the corresponding user data from the database. This is used when
        you need to verify both the validity of the refresh token and the user information.
        """
    ),
]


async def verify_user_permission(user: UserDBDep, route: RequestRouterDep, redis: RedisDep) -> User:
    if not user.is_admin:
        user_permission_list = await redis.get_array(permission_structure.format(user_id=user.id))
        # TODO: If the key does not exist in Redis, fallback to querying the database.
        if route.path not in user_permission_list:
            raise PermissionDeniedException()

    return user
