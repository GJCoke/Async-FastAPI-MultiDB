"""
Author  : Coke
Date    : 2025-04-22
"""

from src.core.route import BaseRoute
from src.deps.database import get_redis_client
from src.schemas.router import FastAPIRouterResponse

router = "interfaceRouter"


async def store_router_in_db(routes: list[BaseRoute]) -> None:
    redis = await get_redis_client()

    router_list_by_db: list[FastAPIRouterResponse] = []
    router_list_by_redis: list[str] = []

    for route in routes:
        if not isinstance(route, BaseRoute):
            continue

        if not route.include_in_schema:
            continue

        custom_route = FastAPIRouterResponse.model_validate(
            {
                "name": route.summary or route.name,
                "methods": route.methods,
                "path": route.path,
                "description": route.description,
            }
        )

        router_list_by_db.append(custom_route)
        router_list_by_redis.append(custom_route.code)

    await redis.set(router, router_list_by_redis)
