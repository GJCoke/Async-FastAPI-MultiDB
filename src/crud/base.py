"""
base file.

Description.

Author : Coke
Date   : 2025-03-18
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy.sql import ColumnElement
from sqlmodel import SQLModel as _SQLModel
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import NotFoundException

SQLModel = TypeVar("SQLModel", bound=_SQLModel)
T = TypeVar("T", bound=_SQLModel)


class BaseCRUD(Generic[SQLModel]):
    def __init__(self, model: type[SQLModel]) -> None:
        self.model = model

    async def get(self, session: AsyncSession, _id: UUID | str, /, *, nullable: bool = True) -> SQLModel:
        """Retrieve a single record from the database by its primary key.

        Args:
            session (AsyncSession): SQLAlchemy session.
            _id (UUID | str): The primary key of the record to be retrieved.
            nullable (bool): If True, allows returning None when the record is not found.
                             If False, raises an exception when the record is not found.
                             Default is True.

        Returns:
            SQLModel: The retrieved record as an instance of the model if found, otherwise None.

        Raises:
            If nullable is False and the record is not found in the database.
        """

        statement = select(self.model).where(self.model.id == _id)
        response = await session.exec(statement)

        if not nullable and not response:
            raise NotFoundException()

        return response.first()

    async def get_by_ids(self, session: AsyncSession, ids: list[UUID | str], /) -> list[SQLModel]:
        statement = select(self.model).where(self.model.id.in_(ids))
        response = await session.exec(statement)

        return response.all() or []

    async def get_count(self, session: AsyncSession) -> int:
        statement = select(func.count()).select_from(self.model)
        response = await session.exec(statement)

        return response.one()

    async def get_paginate(
        self,
        session: AsyncSession,
        /,
        *,
        page: int = 1,
        size: int = 20,
        filters: list[ColumnElement[Any]] | None = None,
        order_by: ColumnElement[Any] | None = None,
    ) -> list[SQLModel]:
        filters = filters or []
        statement = select(self.model).filter(*filters).offset((page - 1) * size).limit(size)

        if order_by is not None:
            statement = statement.order_by(order_by)

        response = await session.exec(statement)

        return response.all() or []


if __name__ == "__main__":

    class User(_SQLModel, table=True):
        id: int
        name: str


    user = BaseCRUD[User](User)


    async def test():
        test = await user.get_paginate(filters=User.id.decs())
        return test
