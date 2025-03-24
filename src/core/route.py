"""
Custom Request and APIRoute class.

Description.

Author : Coke
Date   : 2025-03-12
"""

import logging
from typing import Any

from fastapi.routing import APIRoute

from src.schemas.response import RESPONSES

logger = logging.getLogger(__name__)


class BaseRoute(APIRoute):
    """Custom route class."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Set multiple values for the responses status code.

        You can add response information in RESPONSES,
         but all APIRouter instances need to have route_class set to BaseRoute.

        Similar:
            @app.post("/login", responses={
                400: {"description": "Bad request.", "model": BadRequestResponse},
                422: {"description": "Validation error.", "model": ValidationErrorResponse},
                })
            async def login():
                pass
        """
        kwargs["responses"] = {**RESPONSES, **kwargs.get("responses", {})}
        super().__init__(*args, **kwargs)
