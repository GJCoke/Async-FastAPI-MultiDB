"""
Custom Request and APIRoute class.

Description.

Author : Coke
Date   : 2025-03-12
"""

import re
from typing import Any

from fastapi.routing import APIRoute

from src.schemas.response import RESPONSES


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


def normalize_braced_path_vars(path: str) -> str:
    """
    Replace all `{xxx}` variables in an API path string with a consistent format
    based on the preceding word segment.

    If the preceding segment exists, the variable will be replaced with the singular
    form of that segment followed by `_id`. If no valid segment is found before `{}`,
    it will default to `{id}`.

    This function is useful for automatically generating normalized permission codes
    from FastAPI route paths.

    Args:
        path (str): The API path string, e.g., "/users/{xxx}/menus/{xxx}".

    Returns:
        str: The transformed path with consistent variable naming,
             e.g., "/users/{user_id}/menus/{menu_id}".
    """
    path_parts = path.split("/")

    for index, part in enumerate(path_parts):
        if re.search(r"\{[^{}]+}", part):
            if index > 0 and path_parts[index - 1]:
                singular = path_parts[index - 1].rstrip("s")
                path_parts[index] = f"{{{singular}_id}}"

            else:
                path_parts[index] = "{id}"

    return "/".join(path_parts)


def convert_ids_to_path_vars(path: str) -> str:
    """
    Transform a path by replacing certain path segments with a singular form of the preceding word
    followed by `_id`.

    This function scans the path for segments that match a UUID pattern or a numeric pattern,
    and replaces them with the corresponding `{singular_word_id}` format based on the preceding word.

    Args:
        path (str): The API path string, e.g., "/users/{xxx}/menus/{xxx}".

    Returns:
        str: The transformed path with consistent variable naming,
             e.g., "/users/{user_id}/menus/{menu_id}".
    """
    path_parts = path.split("/")

    for index, part in enumerate(path_parts):
        if re.match(r"[0-9a-fA-F-]{36}", part) or part.isdigit():
            if index > 0 and path_parts[index - 1]:
                singular = path_parts[index - 1].rstrip("s")
                path_parts[index] = f"{{{singular}_id}}"
            else:
                path_parts[index] = "{id}"

    return "/".join(path_parts)
