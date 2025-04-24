"""
Auth schemas.

Why do we separate the request model, response model,
 and database model in our design? Can’t we just use a single model for all purposes?

 - It allows each model to focus on its specific task, making the code easier to maintain.

 - Request and response models leverage Pydantic for data validation, ensuring the data meets the expected structure.

 - Separating request and response models helps to avoid returning sensitive database fields (e.g., password fields),
  enhancing security.

 - You can independently extend or modify each layer without affecting others, such as modifying the database model
  fields while leaving the request and response models unchanged.

 - Having request and response models as distinct layers ensures that all inputs and outputs adhere to
  the defined structure, preventing confusion.

 - The independence of each model makes unit testing easier, as each model has clear responsibilities and functions.

 - The layered design allows for easy replacement, modification, or extension of any layer when needed,
  without affecting others.

Author : Coke
Date   : 2025-03-13
"""

from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from pydantic import EmailStr, Field

from src.schemas import BaseModel, BaseRequest, BaseResponse, ResponseSchema


class UserAccessJWT(BaseRequest):
    """The user information embedded in a JWT access token."""

    user_id: UUID = Field(..., alias="sub")
    name: str
    jti: UUID


class UserRefreshJWT(UserAccessJWT):
    """The user information embedded in a JWT refresh token."""

    agent: str


class LoginRequest(BaseRequest):
    """Login schemas request."""

    username: str
    password: str


class RefreshTokenRequest(BaseRequest):
    """The refresh token schemas request."""

    refresh_token: str


class UserSchema(BaseModel):
    """User schema."""

    name: str
    email: EmailStr
    username: str
    roles: list[str] = []


class UserInfoResponse(UserSchema, ResponseSchema):
    """User info schemas response."""


class UserCreate(UserSchema, BaseRequest):
    """Create user schemas request."""

    is_admin: bool = False
    password: str


class UserUpdate(UserSchema, BaseRequest):
    """Update user schemas request."""


class OAuth2TokenResponse(PydanticBaseModel):
    """OAuth2 token response."""

    access_token: str
    token_type: str


class TokenResponse(BaseResponse):
    """Token response."""

    access_token: str
    refresh_token: str
