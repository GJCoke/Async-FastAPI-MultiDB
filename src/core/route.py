"""
Custom Request and APIRoute class.

Description.

Author : Coke
Date   : 2025-03-12
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

from src.schemas.response import RESPONSES

logger = logging.getLogger(__name__)


class BaseRoute(APIRoute):
    """Custom route class."""

    def __init__(self, *args, **kwargs):
        """Set multiple values for the responses status code.

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

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Used for logging and performance monitoring, helping developers track the details of API requests and
            monitor the response time of each request.

            Args:
                request: Request

            Returns:
                Response
            """
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = round(time.time() - before, 6)
            response.headers["X-Response-Time"] = str(duration)
            logger.debug(
                f"api details. \n"
                f'request url: "{request.method} {request.url}"\n'
                f"request headers: {request.headers}\n"
                f"request query: {request.query_params}\n"
                f"request body: {await request.body()}\n\n"
                f"response duration: {duration}\n"
                f"status code: {response.status_code}\n"
                f"response headers: {response.headers}\n"
                f"response body: {response.body}\n"
            )

            return response

        return custom_route_handler
