"""
config file.

Description.

Author : Coke
Date   : 2025-03-11
"""

from typing import Any

from pydantic import MongoDsn, MySQLDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.environment import Environment


class Config(BaseSettings):
    """Project configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # mysql
    MYSQL_SCHEME: str
    MYSQL_ROOT_USERNAME: str
    MYSQL_ROOT_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str
    REDIS_URL: RedisDsn
    MONGO_URL: MongoDsn

    # current env
    ENVIRONMENT: Environment = Environment.PRODUCTION

    # cors
    CORS_ORIGINS: list[str]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str]

    # version
    APP_VERSION: str = "0.1.0"

    # log
    LOG_LEVEL: str = "INFO"

    @property
    def MYSQL_URL(self) -> MySQLDsn:
        url = (
            f"{self.MYSQL_SCHEME}://{self.MYSQL_ROOT_USERNAME}:{self.MYSQL_ROOT_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

        return MySQLDsn(url=url)


settings = Config()

app_configs: dict[str, Any] = {"title": "FastAPI MultiDB"}

# Disable API documentation if not in the development environment.
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None
