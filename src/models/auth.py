"""
Auth database models.

Author  : Coke
Date    : 2025-04-18
"""

from pydantic import EmailStr

from .base import SQLModel


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"

    name: str
    email: EmailStr
    username: str
    password: bytes
