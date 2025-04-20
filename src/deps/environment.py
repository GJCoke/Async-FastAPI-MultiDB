"""
Author  : Coke
Date    : 2025-04-18
"""

from src.core.config import settings
from src.core.exceptions import NotFoundException


def check_debug() -> None:
    """
    Checks if the current environment is in debug mode.

    This function checks the `ENVIRONMENT.is_debug` setting and raises a
    `NotFoundException` if the environment is not in debug mode.

    Raises:
        NotFoundException: If the current environment is not in debug mode.
    """
    if not settings.ENVIRONMENT.is_debug:
        raise NotFoundException()
