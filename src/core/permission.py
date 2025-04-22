"""
Author  : Coke
Date    : 2025-04-22
"""

from starlette.routing import BaseRoute as StarletteRoute

from src.core.database import AsyncSessionLocal
from src.core.route import BaseRoute
from src.crud.router import RouterCRUD
from src.models.router import InterfaceRouter
from src.schemas.router import FastAPIRouterCreate

router = "interfaceRouter"


async def store_router_in_db(routes: list[StarletteRoute | BaseRoute]) -> None:
    router_list_by_db: list[FastAPIRouterCreate] = []

    for route in routes:
        if not isinstance(route, BaseRoute):
            continue

        if not route.include_in_schema:
            continue

        custom_route = FastAPIRouterCreate.model_validate(
            {
                "name": route.summary or route.name,
                "methods": route.methods,
                "path": route.path,
                "description": route.description,
            }
        )
        router_list_by_db.append(custom_route)

    async with AsyncSessionLocal() as session:
        router_db = RouterCRUD(InterfaceRouter, session=session)
        await router_db.clear_router()
        await router_db.create_app_routers(router_list_by_db)
