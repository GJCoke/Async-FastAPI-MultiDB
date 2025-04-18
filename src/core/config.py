"""
Config settings.

This file holds the project configuration settings loaded from environment variables.

Author : Coke
Date   : 2025-03-11
"""

import os
import re
import secrets
import warnings
from typing import Any

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from pydantic import Field, MongoDsn, PostgresDsn, RedisDsn, Secret, field_validator, model_validator
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict

from src.core.environment import Environment
from src.utils.constants import DAYS, WEEKS
from src.utils.security import generate_rsa_key_pair, load_private_key, serialize_key


class ConfigError(Exception):
    """Config error."""


class BaseSettings(_BaseSettings):
    """Pydantic BaseSettings class."""

    # Pydantic model config for reading from an .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class Config(BaseSettings):
    """Project configuration settings loaded from environment variables."""

    # PostgreSQL configuration settings
    POSTGRESQL_ASYNC_SCHEME: str
    POSTGRESQL_SYNC_SCHEME: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: Secret[str]
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: int = Field(5432, ge=0, le=65535)
    POSTGRESQL_DATABASE: str

    @property
    def ASYNC_DATABASE_POSTGRESQL_URL(self) -> PostgresDsn:
        """Generate and return the postgresql connection URL."""
        return PostgresDsn.build(
            scheme=self.POSTGRESQL_ASYNC_SCHEME,
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD.get_secret_value(),
            host=self.POSTGRESQL_HOST,
            port=self.POSTGRESQL_PORT,
            path=self.POSTGRESQL_DATABASE,
        )

    @property
    def SYNC_DATABASE_POSTGRESQL_URL(self) -> PostgresDsn:
        """Generate and return the postgresql connection URL."""
        return PostgresDsn.build(
            scheme=self.POSTGRESQL_SYNC_SCHEME,
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD.get_secret_value(),
            host=self.POSTGRESQL_HOST,
            port=self.POSTGRESQL_PORT,
            path=self.POSTGRESQL_DATABASE,
        )

    # Redis configuration settings
    REDIS_SCHEME: str = "redis"
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_ROOT_USERNAME: str = ""
    REDIS_ROOT_PASSWORD: Secret[str]
    REDIS_HOST: str
    REDIS_PORT: int = Field(6379, ge=0, le=65535)
    REDIS_DATABASE: int = Field(0, ge=0, le=15)

    @property
    def REDIS_URL(self) -> RedisDsn:
        """Generate and return the Redis connection URL."""
        return RedisDsn.build(
            scheme=self.REDIS_SCHEME,
            username=self.REDIS_ROOT_USERNAME,
            password=self.REDIS_ROOT_PASSWORD.get_secret_value(),
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(self.REDIS_DATABASE),
        )

    CELERY_REDIS_DATABASE: int = Field(1, ge=0, le=15)
    CELERY_TIMEZONE: str = "Asia/Shanghai"

    @property
    def CELERY_REDIS_URL(self) -> RedisDsn:
        """Generate and return the Celery Redis connection URL."""

        return RedisDsn.build(
            scheme=self.REDIS_SCHEME,
            username=self.REDIS_ROOT_USERNAME,
            password=self.REDIS_ROOT_PASSWORD.get_secret_value(),
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(self.CELERY_REDIS_DATABASE),
        )

    # MongoDB configuration settings
    MONGO_SCHEME: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: Secret[str]
    MONGO_HOST: str
    MONGO_PORT: int = Field(27017, ge=0, le=65535)
    MONGO_INITDB_DATABASE: str

    @property
    def DATABASE_MONGO_URL(self) -> MongoDsn:
        """Generate and return the MongoDB connection URL."""
        return MongoDsn.build(
            scheme=self.MONGO_SCHEME,
            username=self.MONGO_INITDB_ROOT_USERNAME,
            password=self.MONGO_INITDB_ROOT_PASSWORD.get_secret_value(),
            host=self.MONGO_HOST,
            port=self.MONGO_PORT,
        )

    # Minio configuration settings
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: Secret[str]

    # Current environment (e.g., TESTING, PRODUCTION)
    ENVIRONMENT: Environment = Environment.PRODUCTION

    # noinspection PyNestedDecorators
    @field_validator("ENVIRONMENT")
    @classmethod
    def environment_validator(cls, environment: Environment) -> Environment:
        """Local environment warn."""
        if environment.value == Environment.LOCAL:
            warnings.warn(
                "The application is currently running in the local environment. "
                "Make sure to update environment-specific settings before deploying to production.",
                RuntimeWarning,
            )
        return environment

    # Cors settings
    CORS_ORIGINS: list[str]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str]

    API_PREFIX_V1: str = "/api/v1"

    # App version
    APP_VERSION: str = "0.1.0"

    # Logging level
    LOG_LEVEL: str = "INFO"


settings = Config()  # type: ignore


class AuthConfig(BaseSettings):
    """Auth configuration."""

    JWT_ALG: str = "HS256"

    ACCESS_TOKEN_KEY: Secret[str]
    ACCESS_TOKEN_EXP: int = 1 * DAYS

    REFRESH_TOKEN_KEY: Secret[str]
    REFRESH_TOKEN_EXP: int = 1 * WEEKS

    RSA_PRIVATE_KEY: RSAPrivateKey
    RSA_PUBLIC_KEY: Secret[str]

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def ensure_keys_config(cls, auth: dict) -> dict:
        """
        Ensures that the ACCESS_TOKEN_KEY and REFRESH_TOKEN_KEY are configured in the environment.
        If the keys are missing, this function will raise an error in a deployed environment
        or generate new ones if not deployed.

        Raises:
            ValueError: If the keys are missing and the application is deployed.
        """
        message = """
            Please configure `{field}` in your `.env` file.
            Do not generate it dynamically at runtime, especially in distributed environments.
            Using a fixed key ensures consistent token verification across multiple services or instances.
        """
        cls.ensure_key_exists(auth, "ACCESS_TOKEN_KEY", message)
        cls.ensure_key_exists(auth, "REFRESH_TOKEN_KEY", message)

        if "RSA_PRIVATE_KEY" not in auth or "RSA_PUBLIC_KEY" not in auth:
            if settings.ENVIRONMENT.is_deployed:
                raise ConfigError(message.format(field="RSA_PRIVATE_KEY or RSA_PUBLIC_KEY"))
            private_key, public_key = generate_rsa_key_pair()

            auth["RSA_PRIVATE_KEY"], auth["RSA_PUBLIC_KEY"] = private_key, serialize_key(public_key)

        else:
            try:
                auth["RSA_PRIVATE_KEY"] = load_private_key(cls.load_rsa_key(auth["RSA_PRIVATE_KEY"]))
                auth["RSA_PUBLIC_KEY"] = cls.load_rsa_key(auth["RSA_PUBLIC_KEY"])
            except Exception as e:
                raise ConfigError(f"""
                        Please check the configuration for `RSA_PRIVATE_KEY` or `RSA_PUBLIC_KEY`.
                        Error: {str(e)}.
                    """)

        return auth

    @classmethod
    def ensure_key_exists(cls, auth: dict, key: str, message: str) -> None:
        """
        Ensures that a specified key exists in the given dictionary `auth`.
        If the key does not exist, it generates a new value using `secrets.token_urlsafe(32)`
        unless the environment is deployed, in which case a ValueError is raised.

        Args:
            auth (dict): The dictionary where the key is checked and potentially added.
            key (str): The key to check for in the `auth` dictionary.
            message (str): The error message format used when raising a ValueError if the key is missing
                           and the environment is deployed.

        Raises:
            ValueError: If the key is missing in the `auth` dictionary and the environment is deployed.

        Returns:
            None: This method does not return anything; it either adds the key to the `auth` dictionary
                  or raises a ValueError.
        """
        if key not in auth:
            if settings.ENVIRONMENT.is_deployed:
                raise ConfigError(message.format(field=key))
            auth[key] = secrets.token_urlsafe(32)

    @classmethod
    def load_rsa_key(cls, key: str) -> str:
        """
        Loads the RSA key from a file if the provided `key` is a file path.
        If the `key` is not a file path, it returns the `key` as is.

        The function checks if the `key` contains a directory separator (e.g., `/` or `\\`),
        and if so, it attempts to read the contents of the file at the given path.
        If the file does not exist, a ValueError is raised.

        Args:
            key (str): The RSA private or public key, either as a file path or as a raw string.

        Raises:
            ValueError: If the file path does not exist when `key` contains directory separators.

        Returns:
            str: The RSA key, either the contents of the file or the raw `key` as provided.
        """
        if re.search(r"[\\/]", key):
            if not os.path.exists(key):
                raise ConfigError("'RSA_PRIVATE_KEY' or 'RSA_PUBLIC_KEY' path does not exist.")

            with open(key, "r", encoding="utf-8") as file:
                return file.read()

        return key


auth_settings = AuthConfig()  # type: ignore

app_configs: dict[str, Any] = {"title": "FastAPI MultiDB"}

# Disable the OpenAPI documentation in non-debug environments
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
