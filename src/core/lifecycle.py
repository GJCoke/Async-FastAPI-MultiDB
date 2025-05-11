"""
FastAPI lifecycle.

Author : Coke
Date   : 2025-03-17
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator
from uuid import UUID

from fastapi import FastAPI
from starlette.routing import BaseRoute as StarletteRoute

from src.core.config import settings
from src.core.database import AsyncSessionLocal, MongoManager, RedisManager
from src.core.route import BaseRoute
from src.crud.router import RouterCRUD
from src.models.router import InterfaceRouter
from src.schemas.router import FastAPIRouterCreate

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    FastAPI lifecycle.
    Args:
        app: FastAPI application.
    """

    RedisManager.connect()
    RedisManager.connect(redis_url=str(settings.CELERY_REDIS_URL), pool_name="celery")

    await MongoManager.connect()
    logger.info("Application startup complete.")

    await store_router_in_db(app.routes)

    yield

    await RedisManager.clear()

    MongoManager.disconnect()
    logger.info("Application shutdown complete.")


async def store_router_in_db(routes: list[StarletteRoute | BaseRoute]) -> None:
    """
    Store the provided routes in the database after filtering and validating them.

    This function processes a list of route objects, validates them, and stores them
    in the database. Only routes that are instances of BaseRoute and are included.

    Args:
        routes (list): A list of route objects (either StarletteRoute or BaseRoute).
    """

    # if not settings.ENVIRONMENT.is_deployed:
    #     return

    app_routes: list[FastAPIRouterCreate] = []

    for route in routes:
        if not isinstance(route, BaseRoute):
            continue

        if not route.include_in_schema:
            continue

        app_routes.append(
            FastAPIRouterCreate.model_validate(
                dict(
                    methods=route.methods,
                    path=route.path,
                    name=route.summary or route.name,
                    description=route.description,
                )
            )
        )

    async with AsyncSessionLocal() as session:
        router_db = RouterCRUD(InterfaceRouter, session=session)
        db_routes = await router_db.get_all()

        add_routes, remove_routes, update_routes = diff_api_routes(db_routes, app_routes)

        if add_routes:
            await router_db.create_all(add_routes)

        if remove_routes:
            await router_db.delete_all(remove_routes)

        if update_routes:
            await router_db.update_all(update_routes)


def diff_api_routes(
    db_routes: list[InterfaceRouter],
    app_routes: list[FastAPIRouterCreate],
) -> tuple[list[FastAPIRouterCreate], list[UUID], list[dict[str, Any]]]:
    """
    Compare two API route lists and return three lists: added routes, removed route IDs, and modified routes.

    Args:
        db_routes (list[InterfaceRouter]): A list of routes stored in the database.
        app_routes (list[InterfaceRouter]): A list of routes in the current application.

    Returns:
        tuple: A tuple containing three elements:
            - added_routes (list[InterfaceRouter]): Routes present in the application but not in the database.
            - removed_routes (list[UUID]): Route IDs present in the database but not in the application.
            - modified_routes (list[dict[str, Any]]): Routes that exist in both the database and application
               but have differences.
               Each dictionary contains the modified attributes (e.g., methods, description, name) and the route's ID.
    """
    old_router = {item.path: item for item in db_routes}
    new_router = {item.path: item for item in app_routes}

    added_routes = []
    removed_routes = []
    modified_routes = []

    # Find the added routes
    for path in new_router:
        if path not in old_router:
            added_routes.append(new_router[path])

    # Find the removed routes
    for path in old_router:
        if path not in new_router:
            removed_routes.append(old_router[path].id)

    # Find the modified routes
    for path in old_router:
        if path in new_router:
            old_route = old_router[path]
            new_route = new_router[path]

            changed_info: dict[str, Any] = {}

            if old_route.methods != new_route.methods:
                changed_info["methods"] = new_route.methods

            if old_route.description != new_route.description:
                changed_info["description"] = new_route.description

            if old_route.name != new_route.name:
                changed_info["name"] = new_route.name

            if changed_info:
                modified_routes.append({**changed_info, "id": old_route.id})

    return added_routes, removed_routes, modified_routes
