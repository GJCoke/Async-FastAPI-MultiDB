"""
Author  : Coke
Date    : 2025-04-22
"""

from sqlmodel import JSON, Column, Field

from src.models.base import SQLModel


class InterfaceRouter(SQLModel, table=True):
    """FastAPI app router model."""

    __tablename__ = "interface_routers"

    name: str = Field(..., unique=True, max_length=100, description="Interface router function name")
    description: str | None = Field(None, description="Interface router function description")
    path: str = Field(..., description="Interface router path")
    methods: list[str] = Field([], sa_column=Column(JSON), description="Interface router methods")
