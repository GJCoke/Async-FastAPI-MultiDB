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

    name: str
    email: EmailStr = Field(..., unique=True)
    username: str = Field(..., unique=True)
    password: bytes
    status: bool = True
    is_admin: bool = False
    roles: list[str] = Field([], sa_column=Column(JSON))


class Role(SQLModel, table=True):
    """Role model."""

    __tablename__ = "roles"

    name: str = Field(..., unique=True)
    description: str
    code: str = Field(..., unique=True)
    status: bool = True
    interface_permissions: list[str] = Field([], sa_column=Column(JSON))
    button_permissions: list[str] = Field([], sa_column=Column(JSON))
    router_permissions: list[str] = Field([], sa_column=Column(JSON))
