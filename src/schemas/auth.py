"""
Auth schemas.

Description.

Author : Coke
Date   : 2025-03-13
"""

from uuid import UUID

from pydantic import EmailStr

from src.schemas.request import BaseRequest


class AuthRequest(BaseRequest):
    username: str
    password: int
    test: bool
    uuid: UUID
    email: EmailStr
    user_id: int
