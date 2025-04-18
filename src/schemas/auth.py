"""
Auth schemas.

Description.

Author : Coke
Date   : 2025-03-13
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.schemas.request import BaseRequest


class JWTUser(BaseRequest):
    """The user information embedded in a JWT token."""

    user_id: UUID = Field(..., alias="sub")
    username: str


class CreateUser(BaseRequest):
    """Create user schemas request."""

    name: str
    email: EmailStr
    username: str
    password: str


class OAuth2TokenResponse(BaseModel):
    """OAuth2 token response."""

    access_token: str
    token_type: str
