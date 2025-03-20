"""
Auth schemas.

Description.

Author : Coke
Date   : 2025-03-13
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr


class AuthRequest(BaseModel):
    username: str
    password: int
    test: bool
    uuid: UUID
    email: EmailStr
