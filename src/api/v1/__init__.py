"""
API v1 router.

Description.

Author : Coke
Date   : 2025-03-10
"""

from fastapi import APIRouter

from src.api.v1 import auth
from src.core.config import settings

v1_router = APIRouter(prefix=settings.API_PREFIX_V1)
v1_router.include_router(auth.router)
