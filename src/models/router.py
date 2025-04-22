"""
Author  : Coke
Date    : 2025-04-22
"""

from sqlmodel import JSON, Column, Field

from src.models.base import SQLModel


class InterfaceRouter(SQLModel):
    __tablename__ = "interface_routers"

    name: str
    description: str
    path: str
    methods: list[str] = Field([], sa_column=Column(JSON))
