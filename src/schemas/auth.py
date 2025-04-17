"""
Auth schemas.

Description.

Author : Coke
Date   : 2025-03-13
"""

from uuid import UUID

from pydantic import Field

from src.schemas.request import BaseRequest


class JWTUser(BaseRequest):
    """The user information embedded in a JWT token."""

    user_id: UUID = Field(..., alias="sub")
    username: str
