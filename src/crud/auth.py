"""
User CRUD logic

This module defines the UserCRUD class responsible for performing
CRUD operations on the `User` model using SQLModel and asynchronous SQLAlchemy sessions.

It provides methods to query user information, such as retrieving a user by their username.

Author : Coke
Date   : 2025-04-18
"""

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import BadRequestException
from src.crud.crud_sqlmodel import BaseSQLModelCRUD
from src.models.auth import User
from src.schemas.auth import UserCreate, UserUpdate


class UserCRUD(BaseSQLModelCRUD[User, UserCreate, UserUpdate]):
    """User CRUD operations using SQLAlchemy."""

    async def get_user_by_username(self, username: str, *, session: AsyncSession | None = None) -> User:
        """
        retrieve a user by their username.

        Args:
            username (str): The username to look up.
            session (AsyncSession | None, optional): Optional database session.
            Defaults to `self. session` if not provided.

        Returns:
            User: The matched user object.

        Raises:
            BadRequestException: If no user is found with the username.
        """

        session = session or self.session

        statement = select(self.model).filter(col(self.model.username) == username)
        result = await session.exec(statement)
        response = result.first()

        if not response:
            raise BadRequestException()

        return response
