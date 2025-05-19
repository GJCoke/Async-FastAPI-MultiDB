"""
Author  : Coke
Date    : 2025-05-19
"""

from fastapi.exceptions import ValidationException
from pydantic import ValidationError


def format_validation_errors(e: ValidationError | ValidationException) -> str:
    """
    Format Pydantic or FastAPI validation errors into a human-readable string.

    Args:
        e (Union[ValidationError, ValidationException]): The exception instance containing validation errors.

    Returns:
        str: A semicolon-separated string describing all validation errors,
             with each error showing its location and message.
    """
    errors = []
    for item in e.errors():
        loc = item.get("loc", ["unknown"])
        loc_str = ".".join(str(part) for part in loc)
        msg = str(item.get("msg", "error.")).lower()
        errors.append(f"{loc_str} {msg}")
    return "; ".join(errors)
