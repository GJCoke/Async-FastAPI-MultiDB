"""
Author  : Coke
Date    : 2025-04-24
"""

from fastapi import Depends
from typing_extensions import Annotated, Doc

from src.core.exceptions import PermissionDeniedException
from src.crud.role import RoleCRUD
from src.deps import RedisDep, SessionDep
from src.deps.auth import UserDBDep
from src.deps.router import RequestRouterDep
from src.models.auth import Role, User

permission_structure = "auth:permission:<{user_id}>"


async def get_role_crud(session: SessionDep) -> RoleCRUD:
    """
    Returns a `RoleCRUD` instance initialized with the provided session.

    Args:
        session (SessionDep): The session dependency to interact with the database.

    Returns:
        RoleCRUD: An instance of the `RoleCRUD` class, initialized with the `Role` model and the provided session.
    """
    return RoleCRUD(Role, session=session)


RoleCrudDep = Annotated[
    RoleCRUD,
    Depends(get_role_crud),
    Doc(
        """
        Dependency for accessing the `RoleCRUD` instance.

        This dependency resolves to an instance of `RoleCRUD` that is used to interact
        with the roles data model in the database. It will be injected into routes that
        require role-based operations.
        """
    ),
]


async def verify_user_permission(user: UserDBDep, route: RequestRouterDep, redis: RedisDep, role: RoleCrudDep) -> User:
    """
    Verifies if the user has permission to access a specific route.

    This function checks if the user has the required permissions to access a specific
    route. If the user is not an admin, it fetches the permissions from Redis or the database,
    depending on the cache state, and verifies if the route is within the user's permissions.

    Args:
        user (UserDBDep): The user whose permissions need to be checked.
        route (RequestRouterDep): The route the user is attempting to access.
        redis (RedisDep): A Redis dependency to cache and retrieve user permissions.
        role (RoleCRUD): The `RoleCRUD` dependency to interact with the roles and their permissions.

    Raises:
        PermissionDeniedException: If the user does not have permission to access the route.

    Returns:
        User: The user model.
    """
    if not user.is_admin:
        redis_key = permission_structure.format(user_id=user.id)
        if await redis.exists(redis_key):
            user_permission_list: list[str] = await redis.get_array(redis_key)

        else:
            roles = await role.get_role_by_codes(user.roles)
            user_permission_list = [permission for role_info in roles for permission in role_info.interface_permissions]
            if user_permission_list:
                await redis.set(redis_key, user_permission_list)

        if route.path not in user_permission_list:
            raise PermissionDeniedException()

    return user


VerifyPermissionDep = Annotated[
    User,
    Depends(verify_user_permission),
    Doc(
        """
        This dependency will invoke the `verify_user_permission` function to check if the user
        has the necessary permissions to access a specific route. It will automatically check
        the user's permissions from the cache (Redis) or fetch them from the database if they
        are not cached.
        """
    ),
]
