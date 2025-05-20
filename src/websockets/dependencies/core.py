"""
Author  : Coke
Date    : 2025-05-20
"""

import inspect
from typing import Any, Awaitable, Callable, Dict

from pydantic._internal._model_construction import ModelMetaclass

from src.websockets.params import SID, Environ

from .utils import get_param_depend


class LifespanContext:
    """Manages teardown functions for async/generator dependencies."""

    def __init__(self) -> None:
        self.teardowns: list[Callable[[], Awaitable[None]]] = []

    async def run_teardowns(self) -> None:
        """Run all registered teardown callbacks in reverse order."""
        for cleanup in reversed(self.teardowns):
            await cleanup()


async def extract_kwargs_from_signature(
    func: Callable,
    context: LifespanContext,
    cache: Dict[Any, Any],
) -> dict[str, Any]:
    """
    Extract keyword arguments required to call a function, resolving dependencies.

    Args:
        func: The function whose parameters are to be resolved.
        context: The lifespan context used to register cleanup tasks.
        cache: A dictionary for caching dependency results.

    Returns:
        A dictionary of keyword arguments with resolved dependencies and injected values.
    """
    sig = inspect.signature(func)
    kwargs: dict[str, Any] = {}
    unknown_params: list[tuple[str, inspect.Parameter]] = []

    for name, param in sig.parameters.items():
        if dep := get_param_depend(param):
            result = await solve_dependency(dep.dependency, context, cache, dep.use_cache)
            kwargs[name] = result

        elif param.annotation in (SID, Environ):
            kwargs[name] = resolve_special_param(param, cache)

        elif param.default != inspect.Parameter.empty:
            kwargs[name] = param.default

        else:
            unknown_params.append((name, param))

    # Automatically infer data argument if unknown parameters exist.
    if unknown_params:
        param_name, param = unknown_params[0]
        kwargs[param_name] = resolve_unknown_param(param, cache)

    return kwargs


def resolve_special_param(param: inspect.Parameter, cache: dict[str, Any]) -> Any:
    """
    Resolve special annotated parameters like SID or Environ.

    Args:
        param: The function parameter being processed.
        cache: The dependency cache.

    Returns:
        The resolved value from the cache.
    """
    key = f"__{param.annotation.__name__.lower()}__"
    return cache.get(key)


def resolve_unknown_param(param: inspect.Parameter, cache: dict[str, Any]) -> Any:
    """
    Resolve unknown parameters using type annotations and cache data.

    Args:
        param: The function parameter being processed.
        cache: The dependency cache containing input data.

    Returns:
        The resolved parameter value, possibly deserialized from data.
    """
    annotation = param.annotation
    if annotation and inspect.isclass(annotation) and isinstance(annotation, ModelMetaclass):
        return annotation(**cache["__data__"])
    return cache["__data__"]


async def run_with_lifespan_handling(
    func: Callable,
    kwargs: dict[str, Any],
    context: LifespanContext,
) -> Any:
    """
    Run a function and register teardown callbacks if it returns a generator.

    Supports:
    - Async generators (with `yield`)
    - Sync generators (with `yield`)
    - Coroutines (async functions)
    - Regular return values

    Args:
        func: The function to call.
        kwargs: The keyword arguments to pass to the function.
        context: The lifespan context to register teardown callbacks.

    Returns:
        The first yielded value (for generators), awaited result (for coroutines),
        or direct return value.
    """
    result = func(**kwargs)

    if inspect.isasyncgen(result):
        value = await result.__anext__()

        async def cleanup() -> None:
            try:
                await result.__anext__()
            except StopAsyncIteration:
                pass

        context.teardowns.append(cleanup)
        return value

    elif inspect.isgenerator(result):
        value = next(result)

        async def cleanup() -> None:
            try:
                next(result)
            except StopIteration:
                pass

        context.teardowns.append(cleanup)
        return value

    elif inspect.iscoroutine(result):
        return await result

    return result


async def solve_dependency(
    func: Callable,
    context: LifespanContext,
    cache: Dict[Any, Any],
    use_cache: bool = True,
) -> Any:
    """
    Resolve a dependency by recursively calling its own dependencies.

    Handles caching and lifecycle teardown registration.

    Args:
        func: The dependency function to resolve.
        context: The lifespan context for managing cleanup.
        cache: A cache to store resolved values.
        use_cache: Whether to use the cache for this dependency.

    Returns:
        The resolved value for the dependency.
    """
    if use_cache and func in cache:
        return cache[func]

    kwargs = await extract_kwargs_from_signature(func, context, cache)

    result = await run_with_lifespan_handling(func, kwargs, context)

    if use_cache:
        cache[func] = result

    return result
