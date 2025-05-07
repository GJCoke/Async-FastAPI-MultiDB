"""
Router API info.

Author  : Coke
Date    : 2025-04-23
"""

from fastapi import APIRouter, Depends

from src.core.route import BaseRoute
from src.deps.role import verify_user_permission
from src.deps.router import RouterCrudDep
from src.schemas.response import Response
from src.schemas.router import FastAPIRouterResponse

router = APIRouter(
    prefix="/router",
    tags=["Router"],
    route_class=BaseRoute,
    dependencies=[Depends(verify_user_permission)],
)


@router.get("/backend")
async def get_router(route: RouterCrudDep) -> Response[list[FastAPIRouterResponse]]:
    """
    This endpoint retrieves all routes from the database and returns them in the response.\f

    Args:
        route (RouterCrudDep): Dependency that handles CRUD operations for routes.

    Returns:
        Response[list[FastAPIRouterResponse]]: A list of FastAPIRouterResponse models, which are
                                                validated and returned as a response.
    """

    routes = await route.get_all()
    return Response(data=[FastAPIRouterResponse.model_validate(_route) for _route in routes])
