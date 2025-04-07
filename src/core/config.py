"""
Config settings.

This file holds the project configuration settings loaded from environment variables.

Author : Coke
Date   : 2025-03-11
"""

from typing import Any

from pydantic import MongoDsn, PostgresDsn, RedisDsn, Secret
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.environment import Environment


class Config(BaseSettings):
    """Project configuration settings loaded from environment variables."""

    # Pydantic model config for reading from an .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # MySQL configuration settings
    POSTGRESQL_SCHEME: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: Secret[str]
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: int = 5432  # Default MySQL port
    POSTGRESQL_DATABASE: str

    # Redis configuration settings
    REDIS_SCHEME: str = "redis"
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_ROOT_USERNAME: str
    REDIS_ROOT_PASSWORD: Secret[str]
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DATABASE: int | None = None

    # MongoDB configuration settings
    MONGO_SCHEME: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: Secret[str]
    MONGO_HOST: str
    MONGO_PORT: int = 27017
    MONGO_INITDB_DATABASE: str

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

    @staticmethod
    def format_url(scheme: str, username: str, password: str, host: str, port: int, database: str = "") -> str:
        """
        Format database url.

        Args:
            scheme (str): database scheme.
            username (str): database username.
            password (str): database password.
            host (str): database host.
            port (int): database port.
            database (str): database name.

        Returns:
            str: DSN
        """
        return "{scheme}://{username}:{password}@{host}:{port}{database}".format(
            scheme=scheme,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
        )

    @property
    def DATABASE_POSTGRESQL_URL(self) -> PostgresDsn:
        """Generate and return the postgresql connection URL."""
        url = self.format_url(
            scheme=self.POSTGRESQL_SCHEME,
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD.get_secret_value(),
            host=self.POSTGRESQL_HOST,
            port=self.POSTGRESQL_PORT,
            database=f"/{self.POSTGRESQL_DATABASE}",
        )
        return PostgresDsn(url=url)

    @property
    def DATABASE_MONGO_URL(self) -> MongoDsn:
        """Generate and return the MongoDB connection URL."""
        url = self.format_url(
            scheme=self.MONGO_SCHEME,
            username=self.MONGO_INITDB_ROOT_USERNAME,
            password=self.MONGO_INITDB_ROOT_PASSWORD.get_secret_value(),
            host=self.MONGO_HOST,
            port=self.MONGO_PORT,
        )
        return MongoDsn(url=url)

    @property
    def REDIS_URL(self) -> RedisDsn:
        """Generate and return the Redis connection URL."""
        url = self.format_url(
            scheme=self.REDIS_SCHEME,
            username=self.REDIS_ROOT_USERNAME if self.REDIS_ROOT_USERNAME else "",
            password=self.REDIS_ROOT_PASSWORD.get_secret_value(),
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            database=f"/{self.REDIS_DATABASE}" if self.REDIS_DATABASE else "",
        )
        return RedisDsn(url=url)


settings = Config()
app_configs: dict[str, Any] = {"title": "FastAPI MultiDB"}

# Disable the OpenAPI documentation in non-debug environments
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
