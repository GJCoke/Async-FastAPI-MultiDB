"""
Author  : Coke
Date    : 2025-04-22
"""

from pydantic import computed_field

from src.schemas.response import BaseResponse


class FastAPIRouterResponse(BaseResponse):
    path: str
    name: str
    description: str
    methods: list[str]

    @property
    @computed_field
    def code(self) -> str:
        return f"{':'.join(self.methods)}:{self.path}"
