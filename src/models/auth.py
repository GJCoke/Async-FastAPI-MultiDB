"""
Auth database models.

Author  : Coke
Date    : 2025-04-18
"""

from pydantic import EmailStr
from sqlmodel import JSON, Column, Field

from .base import SQLModel


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"

    name: str = Field(..., min_length=2, max_length=100, description="User name")
    email: EmailStr = Field(..., unique=True, max_length=254, description="User email address")
    username: str = Field(..., unique=True, min_length=5, max_length=100, description="Username")
    password: bytes
    status: bool = Field(True, description="User status")
    is_admin: bool = Field(False, description="User admin")
    roles: list[str] = Field([], sa_column=Column(JSON), description="User roles code")


class Role(SQLModel, table=True):
    """Role model."""

    __tablename__ = "roles"

    name: str = Field(..., unique=True, min_length=2, max_length=100, description="Role name")
    description: str | None = Field(None, max_length=500, description="Role description")
    code: str = Field(..., unique=True, min_length=5, max_length=100, description="Role code")
    status: bool = Field(True, description="Role status")
    interface_permissions: list[str] = Field([], sa_column=Column(JSON), description="Role interface permissions code")
    button_permissions: list[str] = Field([], sa_column=Column(JSON), description="Role button permissions code")
    router_permissions: list[str] = Field([], sa_column=Column(JSON), description="Role router permissions code")
