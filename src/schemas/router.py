"""
Author  : Coke
Date    : 2025-04-22
"""

from src.schemas import BaseModel, BaseRequest, ResponseSchema


class InterfaceRouterSchema(BaseModel):
    name: str
    description: str
    path: str
    methods: list[str]


class FastAPIRouterResponse(InterfaceRouterSchema, ResponseSchema):
    """Interface router response schema."""


class FastAPIRouterCreate(InterfaceRouterSchema, BaseRequest):
    """Create interface router schema."""


class FastAPIRouterUpdate(InterfaceRouterSchema, BaseRequest):
    """Update interface router schema."""
