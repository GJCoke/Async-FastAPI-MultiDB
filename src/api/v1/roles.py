"""
Author  : Coke
Date    : 2025-04-30
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import col

from src.core.route import BaseRoute
from src.deps.auth import UserDBDep
from src.deps.role import RoleCrudDep, verify_user_permission
from src.models import Role
from src.schemas.response import PaginatedResponse, Response
from src.schemas.role import RoleAllQuery, RoleBatchBody, RoleCreate, RolePageQuery, RoleResponse, RoleUpdate
from src.services.roles import filter_role

router = APIRouter(
    prefix="/roles",
    tags=["Role"],
    route_class=BaseRoute,
    dependencies=[Depends(verify_user_permission)],
)


@router.get("")
async def get_roles(
    query: Annotated[RolePageQuery, Query(...)],
    role_crud: RoleCrudDep,
) -> Response[PaginatedResponse[RoleResponse]]:
    """
    Get a paginated list of roles.\f

    Args:
        query (RolePageQuery): Query parameters including status, keyword, page, and page size.
        role_crud (RoleCrudDep): Dependency that provides CRUD operations for roles.

    Returns:
        Response[PaginatedResponse[RoleResponse]]: Paginated role data.
    """

    filter = filter_role(query.status, query.keyword)
    roles = await role_crud.get_paginate(*filter, page=query.page, size=query.page_size, serializer=RoleResponse)
    return Response(data=roles)


@router.get("/mine")
async def get_my_roles(role_crud: RoleCrudDep, user: UserDBDep) -> Response[list[RoleResponse]]:
    """
    Get roles assigned to the current user.\f

    Args:
        role_crud (RoleCrudDep): Role CRUD dependency.
        user (UserDBDep): Current authenticated user dependency.

    Returns:
        Response[list[RoleResponse]]: List of roles.
    """

    roles = await role_crud.get_all(col(Role.code).in_(user.roles), serializer=RoleResponse)
    return Response(data=roles)


@router.get("/all")
async def get_all_roles(
    query: Annotated[RoleAllQuery, Query(...)],
    role_crud: RoleCrudDep,
) -> Response[list[RoleResponse]]:
    """
    Get a full list of roles without pagination.\f

    Args:
        query (RoleAllQuery): Query parameters including status and keyword.
        role_crud (RoleCrudDep): Role CRUD dependency.

    Returns:
        Response[list[RoleResponse]]: List of roles matching the filters.
    """

    filter = filter_role(query.status, query.keyword)
    roles = await role_crud.get_all(*filter, serializer=RoleResponse)
    return Response(data=roles)


@router.post("")
async def create_role(body: RoleCreate, role_crud: RoleCrudDep) -> Response[RoleResponse]:
    """
    Create a new role.\f

    Args:
        body (RoleCreate): Role creation data.
        role_crud (RoleCrudDep): Role CRUD dependency.

    Returns:
        Response[RoleResponse]: The newly created role.
    """

    role = await role_crud.create(body)
    return Response(data=RoleResponse.model_validate(role))


@router.put("/{role_id}")
async def update_role(role_id: UUID, body: RoleUpdate, role_crud: RoleCrudDep) -> Response[RoleResponse]:
    """
    Update a role by ID.\f

    Args:
        role_id (UUID): ID of the role to update.
        body (RoleUpdate): New role data.
        role_crud (RoleCrudDep): Role CRUD dependency.

    Returns:
        Response[RoleResponse]: The updated role.
    """

    role = await role_crud.update_by_id(role_id, body)
    return Response(data=RoleResponse.model_validate(role))


@router.delete("")
async def batch_delete_role(query: RoleBatchBody, role_crud: RoleCrudDep) -> Response[bool]:
    """
    Delete multiple roles by a list of IDs.\f

    Args:
        query (RoleBatchBody): Contains list of role IDs to delete.
        role_crud (RoleCrudDep): Role CRUD dependency.

    Returns:
        Response[bool]: True if deletion succeeded.
    """

    await role_crud.delete_all(query.ids)
    return Response(data=True)


@router.delete("/{role_id}")
async def delete_role(role_id: UUID, role_crud: RoleCrudDep) -> Response[bool]:
    """
     Delete a single role by ID.\f

    Args:
        role_id (UUID): ID of the role to delete.
        role_crud (RoleCrudDep): Role CRUD dependency.

    Returns:
        Response[bool]: True if deletion succeeded.
    """

    await role_crud.delete(role_id)
    return Response(data=True)
