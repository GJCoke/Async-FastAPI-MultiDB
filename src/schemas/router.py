"""
Author  : Coke
Date    : 2025-04-22
"""

from uuid import UUID

from pydantic import computed_field
from sqlmodel import JSON, Column, Field

from src.core.route import normalize_braced_path_vars
from src.models.router import InterfaceRouter
from src.schemas.response import BaseResponse


class FastAPIRouterResponse(BaseResponse):
    """Interface router response schema."""

    id: UUID
    path: str
    name: str
    description: str
    methods: list[str]

    @computed_field  # type: ignore
    @property
    def code(self) -> str:
        return f"{':'.join(self.methods)}:{normalize_braced_path_vars(self.path)}"


class FastAPIRouterCreate(InterfaceRouter):
    """Create interface router schema."""

    methods: list[str] = Field([], sa_column=Column(JSON))


class FastAPIRouterUpdate(InterfaceRouter):
    """Update interface router schema."""

    methods: list[str] = Field([], sa_column=Column(JSON))
