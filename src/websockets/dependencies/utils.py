"""
This module provides utilities for resolving and converting dependency injection
information from function parameters, including support for both custom `Depends`
and FastAPI-style `Depends`, with compatibility for `Annotated` type hints.

Author  : Coke
Date    : 2025-05-20
"""

import inspect
from typing import Annotated, Any, get_args, get_origin

from src.websockets.params import Depends

FastAPIDepends: Any
try:
    from fastapi.params import Depends as FastAPIDepends  # type: ignore
except ImportError:
    FastAPIDepends = None


def convert_to_depends(obj: Any) -> Depends | None:
    """
    Convert an object to a `Depends` instance.

    This function supports both custom `Depends` and FastAPI `Depends` object.

    Args:
        obj: The object to be converted, possibly a `Depends` or FastAPI Depends.

    Returns:
        A `Depends` instance if conversion is possible, otherwise `None`.
    """
    if isinstance(obj, Depends):
        return obj
    if FastAPIDepends and isinstance(obj, FastAPIDepends):
        return Depends(obj.dependency, use_cache=obj.use_cache)
    return None


def extract_annotated_dependency(annotation: Any) -> Depends | None:
    """
    Extract a dependency from an Annotated type hint.

    Iterates through the metadata in an `Annotated` type and returns the first
    convertible `Depends` instance.

    Args:
        annotation: The type annotation, potentially an `Annotated`.

    Returns:
        A `Depends` instance if found, otherwise `None`.
    """
    if get_origin(annotation) is not Annotated:
        return None

    for metadata in get_args(annotation)[1:]:
        if depend := convert_to_depends(metadata):
            return depend
    return None


def extract_default_dependency(default: Any) -> Depends | None:
    """
    Extract a dependency from a parameter's default value.

    Args:
        default: The default value of the parameter.

    Returns:
        A `Depends` instance if found, otherwise `None`.
    """
    return convert_to_depends(default)


def get_param_depend(param: inspect.Parameter) -> Depends | None:
    """
    Extract dependency information from a function parameter.

    Checks both Annotated metadata and default values to resolve any defined dependencies.

    Args:
        param: The function parameter to inspect.

    Returns:
        A `Depends` instance if a dependency is declared, otherwise `None`.
    """
    if depend := extract_annotated_dependency(param.annotation):
        return depend

    return extract_default_dependency(param.default)
