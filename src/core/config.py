"""
Config settings.

This file holds the project configuration settings loaded from environment variables.

Author : Coke
Date   : 2025-03-11
"""

import secrets
import warnings
from typing import Any

from pydantic import Field, MongoDsn, PostgresDsn, RedisDsn, Secret, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.environment import Environment
from src.utils.constants import DAYS, WEEKS


class Config(BaseSettings):
    """Project configuration settings loaded from environment variables."""

    # Pydantic model config for reading from an .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

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
    def environment_validator(cls, value: Environment) -> Environment:
        if value.value == Environment.LOCAL:
            warnings.warn(
                "The application is currently running in the local environment."
                "Make sure to update environment-specific settings before deploying to production.",
                RuntimeWarning,
            )
        return value

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

    # TODO: add RSA config.

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
        if "ACCESS_TOKEN_KEY" not in auth:
            if settings.ENVIRONMENT.is_deployed:
                raise ValueError(message.format(field="ACCESS_TOKEN_KEY"))
            auth["ACCESS_TOKEN_KEY"] = secrets.token_urlsafe(32)
            secrets.token_hex()

        if "REFRESH_TOKEN_KEY" not in auth:
            if settings.ENVIRONMENT.is_deployed:
                raise ValueError(message.format(field="REFRESH_TOKEN_KEY"))
            auth["REFRESH_TOKEN_KEY"] = secrets.token_urlsafe(32)

        return auth


auth_settings = AuthConfig()  # type: ignore

app_configs: dict[str, Any] = {"title": "FastAPI MultiDB"}

# Disable the OpenAPI documentation in non-debug environments
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
