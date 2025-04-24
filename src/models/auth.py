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
    email: EmailStr
    username: str
    password: bytes
    status: bool = True
    is_admin: bool = False
    roles: list[str] = Field([], sa_column=Column(JSON))


class Role(SQLModel, table=True):
    """Role model."""

    __tablename__ = "roles"

    name: str
    description: str
    code: str
    status: bool = True
    interface_permissions: list[str] = Field([], sa_column=Column(JSON))
    button_permissions: list[str] = Field([], sa_column=Column(JSON))
    router_permissions: list[str] = Field([], sa_column=Column(JSON))
