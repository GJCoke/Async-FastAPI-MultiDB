"""
Authentication service layer

This module contains core authentication logic, including user login,
password decryption, and JWT token generation (access and refresh tokens).
It serves as the business logic layer between the API and the data access layer.

Author  : Coke
Date    : 2025-04-18
"""

import time
from uuid import UUID

from src.core.config import auth_settings
from src.core.database import AsyncRedisClient
from src.core.exceptions import BadRequestException, PermissionDeniedException
from src.crud.auth import UserCRUD
from src.deps.auth import refresh_structure
from src.schemas.auth import TokenResponse, UserAccessJWT, UserRefreshJWT
from src.utils.security import check_password, create_token, decrypt_message
from src.utils.uuid7 import uuid8


def create_access_token(user: UserAccessJWT) -> str:
    """
    Create a JWT access token for the given user.

    Args:
        user (UserAccessJWT): The payload containing user identity information.

    Returns:
        str: Encoded JWT access token.
    """
    return create_token(
        user,
        auth_settings.ACCESS_TOKEN_EXP,
        auth_settings.ACCESS_TOKEN_KEY,
        auth_settings.JWT_ALG,
    )


def create_refresh_token(user: UserRefreshJWT) -> str:
    """
    Create a JWT refresh token for the given user.

    Args:
        user (UserRefreshJWT): The payload containing user identity information.

    Returns:
        str: Encoded JWT refresh token.
    """
    return create_token(
        user,
        auth_settings.REFRESH_TOKEN_EXP,
        auth_settings.REFRESH_TOKEN_KEY,
        auth_settings.JWT_ALG,
    )


def decrypt_password(rsa_password: str) -> str:
    """
    Decrypt an RSA-encrypted password using the configured private key.

    Args:
        rsa_password (str): The encrypted password string (base64-encoded).

    Raises:
        BadRequestException: If decryption fails.

    Returns:
        str: The decrypted plaintext password.
    """
    try:
        password = decrypt_message(auth_settings.RSA_PRIVATE_KEY, rsa_password)
    except Exception:
        raise BadRequestException(detail="Invalid username or password.")

    return password


async def create_user_token(
    user_id: UUID,
    name: str,
    redis: AsyncRedisClient,
    user_agent: str,
) -> TokenResponse:
    """
    Generate a new access token and refresh token for a user.

    This function creates a new access token and refresh token pair,
    stores the refresh token in Redis with an expiration time, and
    returns both tokens in a TokenResponse.

    Args:
        user_id (UUID): The ID of the user.
        name (str): The name of the user.
        redis (AsyncRedisClient): The Redis client used to store the refresh token.
        user_agent (str): The User-Agent header of the current request, used to bind the refresh token to the device.

    Returns:
        TokenResponse: An object containing the access token and refresh token.
    """
    jti = str(uuid8())

    # access token
    token_info = {"sub": user_id, "name": name, "jti": jti}
    access = UserAccessJWT.model_validate(token_info)
    access_token = create_access_token(access)

    # refresh token
    redis_key = refresh_structure.format(user_id=user_id, jti=jti)
    refresh = UserRefreshJWT.model_validate({**token_info, "agent": user_agent})
    refresh_token = create_refresh_token(refresh)
    refresh_value = {
        "token": refresh_token,
        "agent": user_agent,
        "created_at": int(time.time()),
    }

    await redis.set(redis_key, refresh_value, ttl=auth_settings.REFRESH_TOKEN_EXP)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh_user_token(
    user_id: UUID,
    username: str,
    jti: UUID,
    redis: AsyncRedisClient,
    user_agent: str,
) -> TokenResponse:
    """
    Refreshes the user's access and refresh tokens.

    This function verifies the existence of a valid refresh token in Redis,
    deletes the old token to prevent reuse, and generates new access and refresh tokens.

    Args:
        user_id (UUID): The unique identifier of the user.
        username (str): The user's username.
        jti (UUID): The JWT ID of the current refresh token.
        redis (AsyncRedisClient): The Redis client used for token validation and storage.
        user_agent (str): The user agent string from the request headers.

    Returns:
        TokenResponse: An object containing the newly generated access and refresh tokens.

    Raises:
        PermissionDeniedException: If the provided refresh token is invalid or expired.
    """
    redis_key = refresh_structure.format(user_id=user_id, jti=jti)
    if not await redis.exists(redis_key):
        raise PermissionDeniedException()

    await redis.delete(redis_key)

    token = await create_user_token(user_id, username, redis, user_agent)
    return token


async def user_login(
    username: str,
    password: str,
    *,
    user_crud: UserCRUD,
    redis: AsyncRedisClient,
    user_agent: str,
) -> TokenResponse:
    """
    Authenticate the user and return access and refresh tokens.

    Args:
        username (str): The username provided by the client.
        password (str): The RSA-encrypted password provided by the client.
        user_crud (UserCRUD): A CRUD class instance for user-related operations.
        redis (AsyncRedisClient): Redis client to use for authentication.
        user_agent (str): Request object to use for agent.

    Raises:
        BadRequestException: If username does not exist or password is incorrect.

    Returns:
        TokenResponse: JWT access and refresh tokens.
    """

    user_info = await user_crud.get_user_by_username(username)

    decrypted_password = decrypt_password(password)

    if not check_password(decrypted_password, user_info.password):
        raise BadRequestException(detail="Invalid username or password.")

    token = await create_user_token(user_info.id, user_info.name, redis, user_agent)
    return token
