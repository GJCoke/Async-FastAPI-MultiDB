"""
Author  : Coke
Date    : 2025-04-22
"""

from uuid import UUID

from pydantic import computed_field

from src.schemas import BaseModel, BaseRequest, ResponseSchema


class InterfaceRouterSchema(BaseModel):
    """Interface Router Schema."""

    name: str
    description: str
    path: str
    methods: list[str]


class FastAPIRouterResponse(InterfaceRouterSchema, ResponseSchema):
    """Interface router response schema."""

    @computed_field
    def code(self) -> str:
        """Role interface permission code."""
        return f"{':'.join(self.methods)}:{self.path}"


class FastAPIRouterCreate(InterfaceRouterSchema, BaseRequest):
    """Create interface router schema."""


class FastAPIRouterUpdate(InterfaceRouterSchema, BaseRequest):
    """Update interface router schema."""

    id: UUID
