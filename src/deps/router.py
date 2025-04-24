"""
Author  : Coke
Date    : 2025-04-23
"""

from fastapi import Depends, Request
from typing_extensions import Annotated, Doc

from src.core.exceptions import BadRequestException
from src.core.route import BaseRoute
from src.crud.router import RouterCRUD
from src.deps import SessionDep
from src.models.router import InterfaceRouter


async def get_request_router(request: Request) -> BaseRoute:
    """
    Dependency function to retrieve the current route object from the request.

    This is useful for scenarios like permission checks, route-level logging,
    or dynamic route metadata extraction.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        BaseRoute: The route object that matches the current request path.
    """
    route = request.scope.get("route")
    if not isinstance(route, BaseRoute):
        raise BadRequestException()

    return route


async def get_router_crud(session: SessionDep) -> RouterCRUD:
    """
    Provides an instance of RouterCRUD for authentication logic.

    Args:
        session (SessionDep): The database session injected from request context.

    Returns:
        RouterCRUD: An initialized CRUD instance for InterfaceRouter operations.
    """
    return RouterCRUD(InterfaceRouter, session=session)


RequestRouterDep = Annotated[
    BaseRoute,
    Depends(get_request_router),
    Doc(
        """
        The route object for the current request, injected via dependency.

        This can be used for purposes like:
        - Automatic permission code generation
        - Route-level logging and analytics
        - Extracting dynamic metadata from path/method
        """
    ),
]
RouterCrudDep = Annotated[
    RouterCRUD,
    Depends(get_router_crud),
    Doc(
        """
        This dependency uses the `get_router_crud` function to inject a session-based `RouterCRUD`
        instance into the route, allowing for operations such as creating, reading, updating, and deleting
        routers in the context of the authentication logic.
        """
    ),
]
