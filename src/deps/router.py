"""
Author  : Coke
Date    : 2025-04-23
"""

from fastapi import Depends
from typing_extensions import Annotated, Doc

from src.crud.router import RouterCRUD
from src.deps import SessionDep
from src.models.router import InterfaceRouter


async def get_router_crud(session: SessionDep) -> RouterCRUD:
    """
    Provides an instance of RouterCRUD for authentication logic.

    Args:
        session (SessionDep): The database session injected from request context.

    Returns:
        RouterCRUD: An initialized CRUD instance for InterfaceRouter operations.
    """
    return RouterCRUD(InterfaceRouter, session=session)


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
