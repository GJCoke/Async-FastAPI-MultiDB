"""
Author  : Coke
Date    : 2025-05-20
"""

from typing import Callable


class SID:
    """
    Marker class to indicate a 'sid' dependency.

    Used as a type annotation to signal that the parameter
    should be resolved from the socket session ID.

    Examples:
        @sio.on("message")
        async def message(sid: SID):
            print(sid)
    """


class Environ:
    """
    Marker class to indicate an 'environ' dependency.

    Used as a type annotation to signal that the parameter
    should be resolved from the socket environment/context.

    Examples:
        @sio.on("message")
        async def message(environ: Environ):
            print(environ)
    """


class Depends:
    """
    Dependency descriptor class.

    Wraps a callable dependency and optionally indicates
    whether the result should be cached during resolution.

    Args:
        dependency (Callable): The callable to resolve as a dependency.
        use_cache (bool, optional): Whether to cache the dependency result. Defaults to True.

    """

    def __init__(self, dependency: Callable, use_cache: bool = True):
        self.dependency = dependency
        self.use_cache = use_cache
