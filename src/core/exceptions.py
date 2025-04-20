"""
HTTP Exceptions.

This file contains custom HTTP exceptions for the application.

Author : Coke
Date   : 2025-03-13
"""

from typing import Any

from fastapi import status
from fastapi.exceptions import HTTPException


class BaseHTTPException(HTTPException):
    """Base HTTP exception class for general errors."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        *,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = "Http server error.",
        headers: dict[str, str] | None = None,
    ):
        """
        Initializes a custom HTTP exception.

        Args:
            status_code (int): The HTTP status code (default 500).
            detail (Any): The detail message for the exception (default "http server error.").
            headers (dict[str, str] | None): Custom headers to be included in the response (optional).
        """
        super().__init__(status_code, detail, headers)


class BadRequestException(BaseHTTPException):
    """Exception for bad request (400 error)."""

    def __init__(self, *, status_code: int = status.HTTP_400_BAD_REQUEST, detail: str = "bad request."):
        """
        Initializes the BadRequestException.

        Args:
            status_code (int): The HTTP status code for bad request (default 400).
            detail (str): The error message (default "bad request.").
        """
        super().__init__(status_code=status_code, detail=detail)


class UnauthorizedException(BaseHTTPException):
    """Exception for unauthorized (401 error)."""

    def __init__(self, *, status_code: int = status.HTTP_401_UNAUTHORIZED, detail: str = "unauthorized."):
        """
        Initializes the UnauthorizedException.

        Args:
            status_code (int): The HTTP status code for unauthorized (default 401).
            detail (str): The error message (default "unauthorized.").
        """
        super().__init__(status_code=status_code, detail=detail)


class PermissionDeniedException(BaseHTTPException):
    """Exception for permission denial (403 error)."""

    def __init__(self, *, status_code: int = status.HTTP_403_FORBIDDEN, detail: str = "permission denied."):
        """
        Initializes the PermissionDeniedException.

        Args:
            status_code (int): The HTTP status code for permission denial (default 403).
            detail (str): The error message (default "permission denied.").
        """
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(BaseHTTPException):
    """Exception for resource not found (404 error)."""

    def __init__(self, *, status_code: int = status.HTTP_404_NOT_FOUND, detail: str = "not found."):
        """
        Initializes the NotFoundException.

        Args:
            status_code (int): The HTTP status code for not found error (default 404).
            detail (str): The error message (default "not found.").
        """
        super().__init__(status_code=status_code, detail=detail)


class ExistsException(BaseHTTPException):
    """Exception for resource already exists (409 error)."""

    def __init__(self, *, status_code: int = status.HTTP_409_CONFLICT, detail: str = "resource already exists."):
        """
        Initializes the ExistsException.

        Args:
            status_code (int): The HTTP status code for resource already exists error (default 409).
            detail (str): The error message (default "resource already exists.").
        """
        super().__init__(status_code=status_code, detail=detail)
