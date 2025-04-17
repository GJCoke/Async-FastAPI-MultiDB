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
from datetime import UTC, datetime, timedelta

import bcrypt
from authlib.jose import jwt
from authlib.jose.errors import JoseError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from pydantic import Secret

from src.core.config import auth_settings
from src.core.exceptions import UnauthorizedException
from src.schemas.auth import JWTUser


def create_token(
    user: JWTUser,
    *,
    expires_delta: timedelta = timedelta(seconds=auth_settings.ACCESS_TOKEN_EXP),
    key: Secret[str] = auth_settings.ACCESS_TOKEN_KEY,
) -> str:
    """
    Create a JWT access token.

    Args:
        user (JWTUser): The user information to encode in the token.
        expires_delta (timedelta, optional): Token expiration duration. Defaults to configured ACCESS_TOKEN_EXP.
        key (str, optional): Secret key used to sign the JWT. Defaults to ACCESS_TOKEN_KEY from settings.

    Returns:
        str: The generated JWT as a string.
    """
    header = dict(alg=auth_settings.JWT_ALG, typ="JWT")
    payload = user.serializable_dict()
    payload["exp"] = datetime.now(UTC) + expires_delta

    return jwt.encode(header=header, payload=payload, key=key.get_secret_value()).decode("utf-8")


def decode_token(token: str, *, key: Secret[str] = auth_settings.ACCESS_TOKEN_KEY) -> JWTUser:
    """
    Decode and verify a JWT access token, and return the corresponding user info.

    Args:
        token (str): The JWT token string to decode.
        key (str, optional): Secret key used to verify the token signature. Defaults to ACCESS_TOKEN_KEY from settings.

    Returns:
        JWTUser: The user information extracted from the token.

    Raises:
        UnauthorizedException: If the token is invalid or decoding fails.
    """
    try:
        payload = jwt.decode(token, key=key.get_secret_value())
    except JoseError:
        raise UnauthorizedException()

    return JWTUser(**payload)


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
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
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
    if isinstance(key, rsa.RSAPrivateKey):
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def decrypt_public_pem(pem: str) -> PublicKeyTypes:
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
