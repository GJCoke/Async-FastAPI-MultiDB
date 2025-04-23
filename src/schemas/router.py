"""
Author  : Coke
Date    : 2025-04-22
"""

from sqlmodel import JSON, Column, Field

from src.models.router import InterfaceRouter
from src.schemas.response import BaseResponse


class FastAPIRouterResponse(BaseResponse, InterfaceRouter):
    """Interface router response schema."""

    methods: list[str] = Field([], sa_column=Column(JSON))


class FastAPIRouterCreate(InterfaceRouter):
    """Create interface router schema."""

    methods: list[str] = Field([], sa_column=Column(JSON))


class FastAPIRouterUpdate(InterfaceRouter):
    """Update interface router schema."""

    methods: list[str] = Field([], sa_column=Column(JSON))
