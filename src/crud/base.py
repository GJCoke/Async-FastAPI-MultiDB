"""
Database create, read, update, delete operations.

This file contains the base CRUD operations for handling database queries.

Author : Coke
Date   : 2025-03-18
"""

from typing import Any, Generic, Literal, TypeVar, cast, overload
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import ColumnElement
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import ExistsException, NotFoundException
from src.models.base import SQLModel as _SQLModel
from src.schemas.base import BaseModel
from src.schemas.response import PaginatedResponse

SQLModel = TypeVar("SQLModel", bound=_SQLModel)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)
T = TypeVar("T", bound=_SQLModel)


class BaseCRUD(Generic[SQLModel, CreateSchema, UpdateSchema]):
    def __init__(self, model: type[SQLModel]) -> None:
        """
        Initialize the BaseCRUD with a SQLModel.

        Args:
            model (type[SQLModel]): The SQLModel class for the CRUD operations.
        """

        self.model = model

    @property
    def Model(self) -> type[SQLModel]:
        """
        Get the current model class.

        Returns:
            type[SQLModel]: The model class being used in the CRUD operations.
        """

        return self.model

    @overload
    async def get(self, session: AsyncSession, _id: UUID, /, *, nullable: Literal[False]) -> SQLModel: ...

    @overload
    async def get(self, session: AsyncSession, _id: UUID, /, *, nullable: Literal[True]) -> SQLModel | None: ...

    async def get(
        self,
        session: AsyncSession,
        _id: UUID,
        /,
        *,
        nullable: bool = True,
    ) -> SQLModel | None:
        """Retrieve a single record from the database by its primary key.

        Args:
            session (AsyncSession): SQLAlchemy session.
            _id (UUID): The primary key of the record to be retrieved.
            nullable (bool): If True, allows returning None when the record is not found.
                             If False, raises an exception when the record is not found.
                             Default is True.

        Returns:
            SQLModel: The retrieved record as an instance of the model if found, otherwise None.

        Raises:
            NotFoundException: If nullable is False and the record is not found in the database.
        """

        statement = select(self.model).where(self.model.id == _id)
        _response = await session.exec(statement)  # type: ignore
        response = _response.first()

        if not nullable and not response:
            raise NotFoundException(detail=f"{_id} not found.")

        return response

    async def get_by_ids(
        self,
        session: AsyncSession,
        ids: list[UUID],
        /,
    ) -> list[SQLModel]:
        """
        Retrieve multiple records from the database by a list of primary keys.

        Args:
            session (AsyncSession): SQLAlchemy session.
            ids (list[UUID]): List of primary keys to retrieve.

        Returns:
            list[SQLModel]: A list of retrieved records, or an empty list if none are found.
        """

        statement = select(self.model).filter(self.model.id.in_(ids))  # type: ignore
        _response = await session.exec(statement)
        response = cast(list[SQLModel], _response.all())

        return response or []

    async def get_all(
        self,
        session: AsyncSession,
        /,
        *,
        filters: list[ColumnElement[Any]] | None = None,
    ) -> list[SQLModel]:
        """
        Retrieve all records from the database, with optional filters.

        Args:
            session (AsyncSession): SQLAlchemy session.
            filters (list[ColumnElement[Any]] | None): Optional list of filters to apply to the query.

        Returns:
            list[SQLModel]: A list of all records matching the filters.
        """

        filters = filters or []
        statement = select(self.model).filter(*filters)
        _response = await session.exec(statement)
        response = cast(list[SQLModel], _response.all())
        return response

    async def get_count(
        self,
        session: AsyncSession,
        /,
        *,
        filters: list[ColumnElement[Any]] | None = None,
    ) -> int:
        """
        Retrieve the count of records in the database, with optional filters.

        Args:
            session (AsyncSession): SQLAlchemy session.
            filters (list[ColumnElement[Any]] | None): Optional list of filters to apply to the query.

        Returns:
            int: The total number of records matching the filters.
        """

        filters = filters or []
        statement = select(func.count()).select_from(self.model).filter(*filters)
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
        order_by: ColumnElement[Any] | Any | None = None,
    ) -> PaginatedResponse[SQLModel]:
        """
        Retrieve a paginated list of records from the database with optional filters and ordering.

        Args:
            session (AsyncSession): SQLAlchemy session.
            page (int): The page number to retrieve.
            size (int): The number of records per page.
            filters (list[ColumnElement[Any]] | None): Optional list of filters to apply to the query.
            order_by (ColumnElement[Any] | None): Optional column element to order the results.

        Returns:
            PaginatedResponse[SQLModel]: A paginated response containing the records and metadata.
        """

        filters = filters or []
        statement = select(self.model).filter(*filters).offset((page - 1) * size).limit(size)

        if order_by is not None:
            statement = statement.order_by(order_by)

        _response = await session.exec(statement)
        response = cast(list[SQLModel], _response.all() or [])
        total = await self.get_count(session, filters=filters)

        return PaginatedResponse(records=response, total=total, page=page, page_size=size)

    async def create(
        self,
        session: AsyncSession,
        create_in: CreateSchema | SQLModel | dict[str, Any],
        /,
        *,
        validate: bool = True,
    ) -> SQLModel:
        """
        Create a new record in the database.

        Args:
            session (AsyncSession): SQLAlchemy async session for database operations.
            create_in (UpdateSchemaType | SQLModel | dict[str, Any]): Data to create the new record.
                Can be a Pydantic schema, SQLModel instance, or raw dictionary.
            validate (bool, optional): Whether to validate input data before creation. Defaults to True.

        Returns:
            SQLModel: The newly created model instance.

        Raises:
            ExistsException: If a record with conflicting unique constraints already exists.
            ValidationError: If validation fails and validate=True.
        """

        if not validate:
            if not isinstance(create_in, self.model):
                raise ValueError(f"Expected type {type(self.model)} for 'create_in', but got {type(create_in)}.")
        else:
            create_in = self.model.model_validate(create_in)

        try:
            session.add(create_in)
            await session.flush()

            await session.commit()
            await session.refresh(create_in)
        except IntegrityError:
            await session.rollback()
            raise ExistsException()

        return create_in

    async def update(
        self,
        session: AsyncSession,
        current_model: SQLModel,
        update_in: UpdateSchema | SQLModel | dict[str, Any],
    ) -> SQLModel:
        """
        Update an existing model instance with new data.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            current_model (SQLModel): The existing model instance to update.
            update_in (UpdateSchemaType | SQLModel | dict[str, Any]): Update data. Can be schema, model, or dict.
                Only set fields will be updated.

        Returns:
            SQLModel: The updated model instance.

        Note:
            Uses partial update - only fields explicitly set in update_in will be modified.
            None values will be treated as explicit updates unless filtered upstream.
        """

        if not isinstance(update_in, dict):
            update_in = update_in.serializable_dict(exclude_unset=True)

        for field, value in update_in.items():
            setattr(current_model, field, value)

        response = await self.create(session, current_model, validate=False)
        return response

    async def update_by_id(
        self,
        session: AsyncSession,
        _id: UUID,
        update_in: UpdateSchema | dict[str, Any],
        /,
    ) -> SQLModel:
        """
        Update a record by its primary key.

        Args:
            session (AsyncSession): SQLAlchemy async session.
            _id (UUID): Primary key of the record to update.
            update_in (UpdateSchema | dict[str, Any]): Update data.

        Returns:
            SQLModel: The updated model instance.

        Raises:
            NotFoundException: If no record exists with the specified ID.
        """

        response = await self.get(session, _id, nullable=False)
        return await self.update(session, response, update_in)

    async def delete(
        self,
        session: AsyncSession,
        _id: UUID,
        /,
    ) -> SQLModel:
        """
        Delete a record from the database by its primary key.

        Args:
            session (AsyncSession): SQLAlchemy session.
            _id (UUID): The primary key of the record to delete.

        Returns:
            SQLModel: The deleted record.

        Raises:
            NotFoundException: If the record with the specified primary key does not exist.
        """

        response = await self.get(session, _id, nullable=False)
        await session.delete(response)
        await session.commit()
        return response
