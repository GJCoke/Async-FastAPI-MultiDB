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
    REDIS_URL: RedisDsn
    MONGO_URL: MongoDsn

    # Current environment (e.g., TESTING, production)
    ENVIRONMENT: Environment = Environment.PRODUCTION

    # Cors settings
    CORS_ORIGINS: list[str]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str]

    API_PREFIX_V1 = "/api/v1"

    # App version
    APP_VERSION: str = "0.1.0"

    # Logging level
    LOG_LEVEL: str = "INFO"

    @property
    def MYSQL_URL(self) -> MySQLDsn:
        """Generate and return the MySQL connection URL."""
        url = (
            f"{self.MYSQL_SCHEME}://{self.MYSQL_ROOT_USERNAME}:{self.MYSQL_ROOT_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

        return MySQLDsn(url=url)


settings = Config()

app_configs: dict[str, Any] = {"title": "FastAPI MultiDB"}

# Disable the OpenAPI documentation in non-debug environments
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
