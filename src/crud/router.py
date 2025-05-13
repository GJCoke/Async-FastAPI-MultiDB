"""
router file.

Description.

Author : Coke
Date   : 2025-04-22
"""

from typing import Any

from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.crud_sqlmodel import BaseSQLModelCRUD
from src.models.router import InterfaceRouter
from src.schemas.router import FastAPIRouterCreate, FastAPIRouterUpdate


class RouterCRUD(BaseSQLModelCRUD[InterfaceRouter, FastAPIRouterCreate, FastAPIRouterUpdate]):
    """Router CRUD operations using SQLAlchemy."""

    async def clear_router(self, *, session: AsyncSession | None = None) -> None:
        """
        Delete all records from the associated router model table.

        Args:
            session (AsyncSession | None): Optional SQLAlchemy async session. If not provided, uses the default session.
        """
        session = session or self.session

        statement = delete(self.model)
        await session.exec(statement)  # type: ignore
        await self.commit()

    async def create_app_routers(
        self,
        routes: list[FastAPIRouterCreate] | list[dict[str, Any]],
        *,
        session: AsyncSession | None = None,
    ) -> None:
        """
        Batch insert multiple router records into the database.

        Args:
            routes (list[FastAPIRouterCreate]): A list of route creation schema instances to be inserted.
            session (AsyncSession | None): Optional SQLAlchemy async session. If not provided, uses the default session.
        """
        session = session or self.session

        session.add_all([self.model.model_validate(route) for route in routes])
        await self.commit()
