"""
Author  : Coke
Date    : 2025-04-22
"""

from pydantic import computed_field

from src.core.route import normalize_braced_path_vars
from src.schemas.request import BaseRequest
from src.schemas.response import BaseResponse


class FastAPIRouterResponse(BaseResponse):
    path: str
    name: str
    description: str
    methods: list[str]

    @computed_field  # type: ignore
    @property
    def code(self) -> str:
        return f"{':'.join(self.methods)}:{normalize_braced_path_vars(self.path)}"


class FastAPIRouterCreate(BaseRequest):
    path: str
    name: str
    description: str
    methods: list[str]


class FastAPIRouterUpdate(BaseRequest):
    """update"""
