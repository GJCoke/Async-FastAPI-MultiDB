"""
Config settings.

This file holds the project configuration settings loaded from environment variables.

Author : Coke
Date   : 2025-03-11
"""

from typing import Any

from pydantic import Field, MongoDsn, PostgresDsn, RedisDsn, Secret
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.environment import Environment


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
app_configs: dict[str, Any] = {"title": "FastAPI MultiDB"}

# Disable the OpenAPI documentation in non-debug environments
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
