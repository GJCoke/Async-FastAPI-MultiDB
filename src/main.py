"""
FastAPI entry point.

This is the main entry point for the FastAPI application. It sets up the middleware,
routes, and exception handling for the application.

Author : Coke
Date   : 2025-03-10
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from src.api.v1 import v1_router
from src.core.config import app_configs, settings
from src.schemas.response import Response as SchemaResponse
from src.schemas.response import ServerErrorResponse, ValidationErrorResponse

logger = logging.getLogger("app")

app = FastAPI(**app_configs)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

app.include_router(v1_router)


@app.exception_handler(Exception)
async def handle_server_errors(_: Request, exc: Exception) -> JSONResponse:
    """Capture all non-deliberate exceptions and respond with a 500 status code."""

    logger.exception(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ServerErrorResponse(data=str(exc)).serializable_dict(),
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_errors(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Capture parameter exception errors and process their structure."""

    errors = [
        f"{item.get('loc', [..., 'unknown'])[1]} {str(item.get('msg', 'error.')).lower()}" for item in exc.errors()
    ]
    details = "; ".join(errors)
    logger.debug(f"validation errors: {details}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationErrorResponse(data=details).serializable_dict(),
    )


@app.exception_handler(HTTPException)
async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
    """Custom handler for HTTP exceptions."""

    return JSONResponse(
        status_code=exc.status_code,
        content=SchemaResponse(code=exc.status_code, message=str(exc.detail)).serializable_dict(),
    )
