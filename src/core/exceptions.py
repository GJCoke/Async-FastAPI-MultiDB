"""
exceptions file.

Description.

Author : Coke
Date   : 2025-03-13
"""

from typing import Any

from fastapi import status
from fastapi.exceptions import HTTPException


class BaseHTTPException(HTTPException):
    """base http exception class."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        *,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = "http server error.",
        headers: dict[str, str] | None = None,
    ):
        super().__init__(status_code, detail, headers)


class PermissionDeniedException(BaseHTTPException):
    """permission denied exception."""

    def __init__(self, *, status_code: int = 403, detail: str = "permission denied."):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(BaseHTTPException):
    """not found exception."""

    def __init__(self, *, status_code: int = status.HTTP_404_NOT_FOUND, detail: str = "not found."):
        super().__init__(status_code=status_code, detail=detail)
