"""
Author  : Coke
Date    : 2025-04-24
"""

from uuid import UUID

from src.schemas import BaseModel, BaseRequest, ResponseSchema
from src.schemas.request import BatchRequest, PaginatedRequest


class RoleSchema(BaseModel):
    """Role Schema."""

    name: str
    description: str
    code: str
    status: bool = True
    interface_permissions: list[str] = []
    button_permissions: list[str] = []
    router_permissions: list[str] = []


class RoleResponse(RoleSchema, ResponseSchema):
    """Role response schema."""

    id: UUID


class RoleCreate(RoleSchema, BaseRequest):
    """Create role schema."""


class RoleUpdate(RoleSchema, BaseRequest):
    """Update role schema."""


class RoleQueriesSchema(BaseModel):
    """Queries role schema."""

    keyword: str = ""
    status: bool | None = None


class RolePageQuery(RoleQueriesSchema, PaginatedRequest):
    """Queries page role schema."""


class RoleAllQuery(RoleQueriesSchema):
    """Queries all role schema."""


class RoleBatchBody(BatchRequest):
    """Queries batch role schema."""
