"""
FastAPI entry point.

This is the main entry point for the FastAPI application. It sets up the middleware,
routes, and exception handling for the application.

Author : Coke
Date   : 2025-03-10
"""

import logging
import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.datastructures import Address
from starlette.exceptions import HTTPException

from src.api.v1 import v1_router
from src.core.config import app_configs, settings
from src.core.lifecycle import lifespan
from src.schemas.response import Response as SchemaResponse
from src.schemas.response import ServerErrorResponse, ValidationErrorResponse

logger = logging.getLogger(__name__)

app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

app.include_router(v1_router)


def get_client_addr(client: Address | None) -> str:
    """
    Get the client address.
    Args:
        client(Address | None): Starlette client address.
    """
    if not client:
        return ""
    return "%s:%d" % client


@app.middleware("http")
async def http_middleware(request: Request, callback: Callable[[Request], Awaitable[Response]]) -> Response:
    """
    Middleware function that measures the time taken to process a request
    and logs the request method, URL path, response status, and duration.

    Args:
        request (Request): The incoming HTTP request.
        callback (Callable[[Request], Awaitable[Response]]): The callback func to process the request and response.

    Returns:
        Response: The HTTP response returned to the client after processing.
    """
    before = time.time()
    response = await callback(request)

    duration = round((time.time() - before) * 1000)
    logger.info(
        '%s - "%s %s HTTP/%s" %d %dms',
        get_client_addr(request.client),
        request.method,
        request.url.path,
        request.scope.get("http_version"),
        response.status_code,
        duration,
    )

    return response


@app.exception_handler(Exception)
async def handle_server_errors(request: Request, exc: Exception) -> JSONResponse:
    """Capture all non-deliberate exceptions and respond with a 500 status code."""

    logger.error(
        '"%s %s" %d ServerException: %s',
        request.method,
        request.url.path,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ServerErrorResponse(data=str(exc)).serializable_dict(),
    )


@app.exception_handler(RequestValidationError)
async def handle_request_validation_errors(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Capture parameter exception errors and process their structure."""

    errors = [
        f"{item.get('loc', [..., 'unknown'])[-1]} {str(item.get('msg', 'error.')).lower()}" for item in exc.errors()
    ]
    details = "; ".join(errors)
    logger.warning(
        '"%s %s" RequestValidationError: %s',
        request.method,
        request.url.path,
        details,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationErrorResponse(data=details).serializable_dict(),
    )


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom handler for HTTP exceptions."""

    logger.error(
        '"%s %s" %d HTTPException: %s',
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=SchemaResponse(code=exc.status_code, message=str(exc.detail)).serializable_dict(),
    )
