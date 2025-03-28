"""
Config settings.

This file holds the project configuration settings loaded from environment variables.

Author : Coke
Date   : 2025-03-11
"""

from typing import Any

from pydantic import MongoDsn, MySQLDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.environment import Environment


class Config(BaseSettings):
    """Project configuration settings loaded from environment variables."""

    # Pydantic model config for reading from an .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # MySQL configuration settings
    MYSQL_SCHEME: str
    MYSQL_ROOT_USERNAME: str
    MYSQL_ROOT_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int = 3306  # Default MySQL port
    MYSQL_DATABASE: str

    # Redis configuration settings
    REDIS_SCHEME: str = "redis"
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_ROOT_USERNAME: str
    REDIS_ROOT_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DATABASE: int | None = None
    MONGO_URL: MongoDsn

    # Current environment (e.g., TESTING, production)
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
    def format_url(scheme: str, username: str, password: str, host: str, port: int, database: str) -> str:
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
    def MYSQL_URL(self) -> MySQLDsn:
        """Generate and return the MySQL connection URL."""
        url = self.format_url(
            scheme=self.MYSQL_SCHEME,
            username=self.MYSQL_ROOT_USERNAME,
            password=self.MYSQL_ROOT_PASSWORD,
            host=self.MYSQL_HOST,
            port=self.MYSQL_PORT,
            database=f"/{self.MYSQL_DATABASE}",
        )
        return MySQLDsn(url=url)

    @property
    def REDIS_URL(self) -> RedisDsn:
        """Generate and return the MySQL connection URL."""
        url = self.format_url(
            scheme=self.REDIS_SCHEME,
            username=self.REDIS_ROOT_USERNAME,
            password=self.REDIS_ROOT_PASSWORD,
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
