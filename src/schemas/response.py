"""
Response model schemas.

Author : Coke
Date   : 2025-03-12
"""

import time
from typing import Any, Generic, TypeVar

from fastapi import status
from pydantic import ConfigDict, Field

from .base import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response model."""

    model_config = ConfigDict(**(BaseModel.model_config or {}), from_attributes=True)


class Response(BaseResponse, Generic[T]):
    """
    Unified response.

    Examples:
        @router.get("/user")
        def user() -> Response[UserInfo]:
            pass
    """

    code: int = Field(status.HTTP_200_OK, description="status code.")
    message: str = Field("Successful.")
    ts: int = Field(int(time.time()), description="current server time.")
    data: T | None = Field(None, description="response data.")

    def __init__(self, /, **kwargs: Any):
        super().__init__(**kwargs)
        self.ts = int(time.time())


class PaginatedResponse(BaseResponse, Generic[T]):
    """
    Unified paginated response.

    Examples:
        @router.get("/user")
        def user() -> Response[PaginatedResponse[UserInfo]]:
            pass

        {
          "code": 200,
          "message": "Successful.",
          "ts": 1741789270,
          "data": {
            "page": 1,
            "pageSize": 20,
            "total": 100,
            "records": []
          }
        }
    """

    page: int = Field(..., description="page number.")
    page_size: int = Field(..., description="number of items per page.")
    total: int = Field(..., description="total number of items.")
    records: list[T] = Field([], description="records.")


class BadRequestResponse(Response):
    """Unified Bad request response."""

    code: int = status.HTTP_400_BAD_REQUEST
    message: str = "Bad Request."
    data: None = None


class AuthenticationError(Response):
    """Authentication error response."""

    code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Invalid credentials."
    data: None = None


class PermissionResponse(Response):
    """Unified permission response."""

    code: int = status.HTTP_403_FORBIDDEN
    message: str = "Permission denied."
    data: None = None


class NotFoundResponse(Response):
    """Unified not found response."""

    code: int = status.HTTP_404_NOT_FOUND
    message: str = "Not found."
    data: None = None


class ValidationErrorResponse(Response):
    """Unified unprocessable entity response."""

    code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    message: str = "Validation error."
    data: str = "Validation error details."


class ServerErrorResponse(Response):
    """Unified server error response."""

    code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Internal Server Error."
    data: str = "Internal Server Error details."


RESPONSES = {
    400: {"description": "Bad Request.", "model": BadRequestResponse},
    401: {"description": "Unauthorized.", "model": AuthenticationError},
    403: {"description": "Permission denied.", "model": PermissionResponse},
    404: {"description": "Not found.", "model": NotFoundResponse},
    422: {"description": "Unprocessable Entity.", "model": ValidationErrorResponse},
    500: {"description": "Internal Server Error.", "model": ServerErrorResponse},
}
