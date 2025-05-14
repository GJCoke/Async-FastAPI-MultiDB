"""
Login testcase.

Author : Coke
Date   : 2025-05-07
"""

import pytest
import pytest_asyncio
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import status
from httpx import AsyncClient
from redis.asyncio import Redis


@pytest_asyncio.fixture
async def rsa_public_key(client: AsyncClient) -> RSAPublicKey:
    """
    Fetches the public RSA key used for encryption.

    This fixture sends a GET request to the /auth/keys/public endpoint to
    retrieve the public key and loads it as an RSAPublicKey object.

    Args:
        client (AsyncClient): The HTTP client used to interact with the FastAPI app.

    Returns:
        RSAPublicKey: The public RSA key used for encryption.
    """
    from src.utils.security import load_public_pem

    response = await client.get("/auth/keys/public")
    assert response.status_code == 200
    pem = response.json()["data"]
    public_key = load_public_pem(pem)
    assert isinstance(public_key, RSAPublicKey)
    return public_key


@pytest.mark.asyncio
async def test_public_key(client: AsyncClient) -> None:
    """
    Tests if the public key retrieval works correctly.

    This test sends a GET request to the /auth/keys/public endpoint to ensure
    that the server responds with a valid public RSA key.

    Args:
        client (AsyncClient): The HTTP client used to interact with the FastAPI app.
    """
    from src.utils.security import load_public_pem

    response = await client.get("/auth/keys/public")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK

    pem = response.json()["data"]
    public_key = load_public_pem(pem)
    assert isinstance(public_key, RSAPublicKey)


@pytest.mark.asyncio
async def test_login(client: AsyncClient, rsa_public_key: RSAPublicKey, redis: Redis) -> None:
    """
    Tests the login functionality using an encrypted password.

    This test sends a POST request to the /auth/login endpoint with a
    username and an encrypted password. It then checks if the response is
    successful and validates the returned token.

    Args:
        client (AsyncClient): The HTTP client used to interact with the FastAPI app.
        rsa_public_key (RSAPublicKey): The public RSA key used for encrypting the password.
    """
    from src.core.config import auth_settings
    from src.deps.auth import refresh_structure
    from src.initdb import PASSWORD, USERNAME
    from src.schemas.auth import TokenResponse, UserInfoResponse
    from src.utils.security import decode_token, encrypt_message

    response = await client.post(
        "/auth/login",
        json={"username": USERNAME, "password": encrypt_message(rsa_public_key, PASSWORD)},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["code"] == status.HTTP_200_OK
    token_response = TokenResponse.model_validate(response.json()["data"])
    access_token = decode_token(token_response.access_token, auth_settings.ACCESS_TOKEN_KEY)
    refresh_token = decode_token(token_response.refresh_token, auth_settings.REFRESH_TOKEN_KEY)

    user_response = await client.get(
        "/auth/user/info", headers={"Authorization": f"Bearer {token_response.access_token}"}
    )
    assert user_response.status_code == status.HTTP_200_OK
    assert user_response.json()["code"] == status.HTTP_200_OK
    user_info = UserInfoResponse.model_validate(user_response.json()["data"])

    redis_key = refresh_structure.format(user_id=user_info.id, jti=access_token.jti)
    redis_refresh = await redis.hgetall(redis_key)
    assert redis_refresh["token"] == token_response.refresh_token
    assert redis_refresh["agent"] == refresh_token.agent
