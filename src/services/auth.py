"""
Authentication service layer

This module contains core authentication logic, including user login,
password decryption, and JWT token generation (access and refresh tokens).
It serves as the business logic layer between the API and the data access layer.

Author  : Coke
Date    : 2025-04-18
"""

from src.core.config import auth_settings
from src.core.exceptions import BadRequestException
from src.crud.auth import UserCRUD
from src.schemas.auth import TokenResponse, UserJWT
from src.utils.security import check_password, create_token, decrypt_message


def create_access_token(user: UserJWT) -> str:
    """
    Create a JWT access token for the given user.

    Args:
        user (UserJWT): The payload containing user identity information.

    Returns:
        str: Encoded JWT access token.
    """
    return create_token(
        user,
        auth_settings.ACCESS_TOKEN_EXP,
        auth_settings.ACCESS_TOKEN_KEY,
        auth_settings.JWT_ALG,
    )


def create_refresh_token(user: UserJWT) -> str:
    """
    Create a JWT refresh token for the given user.

    Args:
        user (UserJWT): The payload containing user identity information.

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


async def user_login(username: str, password: str, *, user_crud: UserCRUD) -> TokenResponse:
    """
    Authenticate the user and return access and refresh tokens.

    Args:
        username (str): The username provided by the client.
        password (str): The RSA-encrypted password provided by the client.
        user_crud (UserCRUD): A CRUD class instance for user-related operations.

    Raises:
        BadRequestException: If username does not exist or password is incorrect.

    Returns:
        TokenResponse: JWT access and refresh tokens.
    """
    user_info = await user_crud.get_user_by_username(username)

    decrypted_password = decrypt_password(password)

    if not check_password(decrypted_password, user_info.password):
        raise BadRequestException(detail="Invalid username or password.")
    user = UserJWT(sub=user_info.id, name=user_info.name)  # type: ignore

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )
