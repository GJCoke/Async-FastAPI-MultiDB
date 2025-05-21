"""
Security utilities for authentication and authorization.

This module provides functionality for:

- JWT (JSON Web Token): Create and decode secure tokens for user authentication.
- Password Hashing: Securely hash and verify passwords using bcrypt.
- RSA Encryption: Support for RSA key-based signing and verification for JWT or other sensitive data.

Author : Coke
Date   : 2025-04-17
"""

import base64
import logging
from datetime import timedelta
from typing import overload

import bcrypt
from authlib.jose import jwt
from authlib.jose.errors import JoseError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey, generate_private_key
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from pydantic import SecretStr

from src.core.exceptions import UnauthorizedException
from src.schemas.auth import UserAccessJWT, UserRefreshJWT
from src.utils.date import get_current_utc_time

logger = logging.getLogger(__name__)


class AccessSecret(SecretStr):
    """Custom secret type for Access Token."""

    def __str__(self) -> str:
        return "AccessSecret(**********)"


class RefreshSecret(SecretStr):
    """Custom secret type for Refresh Token."""

    def __str__(self) -> str:
        return "RefreshSecret(**********)"


def create_token(
    user: UserAccessJWT,
    expires_delta: timedelta,
    key: AccessSecret | RefreshSecret,
    alg: str,
) -> str:
    """
    Create a JWT access token.

    Args:
        user (UserAccessJWT): The user information to encode in the token.
        expires_delta (timedelta): Token expiration duration. Defaults to configured ACCESS_TOKEN_EXP.
        key (AccessSecret | RefreshSecret): Secret key used to sign the JWT. Defaults to ACCESS_TOKEN_KEY from settings.
        alg (str): Secret algorithm used to sign the JWT. Defaults to 'RS256'.

    Returns:
        str: The generated JWT as a string.
    """
    header = dict(alg=alg, typ="JWT")
    payload = user.serializable_dict()
    payload["exp"] = get_current_utc_time() + expires_delta

    return jwt.encode(header=header, payload=payload, key=key.get_secret_value()).decode("utf-8")


@overload
def decode_token(token: str, key: AccessSecret) -> UserAccessJWT: ...


@overload
def decode_token(token: str, key: RefreshSecret) -> UserRefreshJWT: ...


def decode_token(token: str, key: AccessSecret | RefreshSecret) -> UserAccessJWT | UserRefreshJWT:
    """
    Decode and verify a JWT access token, and return the corresponding user info.

    Args:
        token (str): The JWT token string to decode.
        key (AccessSecret | RefreshSecret): Secret key used to verify the token signature.

    Returns:
        UserAccessJWT: The user information extracted from the token.

    Raises:
        UnauthorizedException: If the token is invalid or decoding fails.
    """
    try:
        payload = jwt.decode(token, key=key.get_secret_value())
        payload.validate()
    except JoseError:
        logger.exception("Invalid JWT token: %s", token)
        raise UnauthorizedException()

    return UserAccessJWT(**payload) if isinstance(key, AccessSecret) else UserRefreshJWT(**payload)


def hash_password(password: str) -> bytes:
    """
    Hash the given plaintext password using bcrypt.

    Args:
        password (str): The plaintext password to be hashed.

    Returns:
        bytes: The hashed password with salt applied.
    """
    bytes_password = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(bytes_password, salt)


def check_password(password: str, hashed_password: bytes) -> bool:
    """
    Verify a plaintext password against the hashed password.

    Args:
        password (str): The plaintext password to verify.
        hashed_password (bytes): The previously hashed password.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    bytes_password = bytes(password, "utf-8")
    return bcrypt.checkpw(bytes_password, hashed_password)


def generate_rsa_key_pair() -> tuple[RSAPrivateKey, RSAPublicKey]:
    """
    Generate an RSA private and public key pair.

    Returns:
        tuple[RSAPrivateKey, RSAPublicKey]: A tuple containing the generated RSA private key and public key.
    """
    private_key = generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    return private_key, public_key


def serialize_key(key: RSAPrivateKey | RSAPublicKey) -> bytes:
    """
    Serialize an RSA key (private or public) to PEM format.

    Args:
        key (RSAPrivateKey | RSAPublicKey): The RSA key to serialize.

    Returns:
        bytes: The PEM-encoded bytes of the key.
    """
    if isinstance(key, RSAPrivateKey):
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def load_public_pem(pem: str) -> PublicKeyTypes:
    """
    Load a public key from a PEM-encoded string.

    Args:
        pem (str): The PEM-formatted public key string.

    Returns:
        PublicKeyTypes: The loaded public key object.
    """
    return load_pem_public_key(pem.encode("utf-8"))


def load_private_key(pem: str, password: bytes | None = None) -> PrivateKeyTypes:
    """
    Load an RSA private key from a PEM-formatted string.

    Args:
        pem (str): PEM-encoded private key string.
        password (bytes, optional): Password if the PEM is encrypted. Defaults to None.

    Returns:
        PrivateKeyTypes: The loaded RSA private key object.
    """
    return load_pem_private_key(pem.encode("utf-8"), password=password)


def encrypt_message(public_key: RSAPublicKey, message: str) -> str:
    """
    Encrypt a message using an RSA public key.

    Args:
        public_key (RSAPublicKey): The RSA public key used for encryption.
        message (str): The plain text message to encrypt.

    Returns:
        str: The base64-encoded encrypted message.
    """
    encrypted_message = public_key.encrypt(
        message.encode("utf-8"),
        padding.PKCS1v15(),
    )

    return base64.b64encode(encrypted_message).decode("utf-8")


def decrypt_message(private_key: RSAPrivateKey, encrypted_message: str) -> str:
    """
    Decrypt an encrypted message using an RSA private key.

    Args:
        private_key (RSAPrivateKey): The RSA private key used for decryption.
        encrypted_message (str): The base64-encoded encrypted message.

    Returns:
        str: The decrypted plain text message.
    """
    decrypted_message = private_key.decrypt(
        base64.b64decode(encrypted_message),
        padding.PKCS1v15(),
    )
    return decrypted_message.decode("utf-8")


if __name__ == "__main__":
    __private_key, __public_key = generate_rsa_key_pair()
    _private_key, _public_key = serialize_key(__private_key), serialize_key(__public_key)
    with open("private.pem", "wb") as private_key_file:
        private_key_file.write(_private_key)

    with open("public.pem", "wb") as public_key_file:
        public_key_file.write(_public_key)
