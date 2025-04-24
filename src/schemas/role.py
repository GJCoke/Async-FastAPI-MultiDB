"""
Author  : Coke
Date    : 2025-04-24
"""

from uuid import UUID

from src.schemas import BaseModel, BaseRequest, ResponseSchema


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


class RoleCreate(RoleSchema, BaseRequest):
    """Create role schema."""


class RoleUpdate(RoleSchema, BaseRequest):
    """Update role schema."""

    id: UUID
