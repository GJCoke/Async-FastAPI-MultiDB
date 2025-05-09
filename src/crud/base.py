"""
Database create, read, update, delete operations.

This file contains the base CRUD operations for handling database queries.

Author : Coke
Date   : 2025-03-18
"""

from typing import Any, Generic, Literal, Sequence, TypeVar, cast, overload
from uuid import UUID

from beanie import PydanticObjectId
from beanie.odm.enums import SortDirection
from beanie.operators import In
from motor.motor_asyncio import AsyncIOMotorClientSession
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import ColumnElement
from sqlmodel import col, delete, func, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.exceptions import ExistsException, NotFoundException
from src.models.base import Document as _Document
from src.models.base import SQLModel as _SQLModel
from src.schemas.base import BaseModel
from src.schemas.response import PaginatedResponse

SQLModel = TypeVar("SQLModel", bound=_SQLModel)
Document = TypeVar("Document", bound=_Document)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)
T = TypeVar("T", bound=_SQLModel)
_PydanticBaseModel = TypeVar("_PydanticBaseModel", bound=PydanticBaseModel)


class BaseSQLModelCRUD(Generic[SQLModel, CreateSchema, UpdateSchema]):
    """
    Base class for SQL CRUD operations using SQLAlchemy.

    This class provides generic CRUD operations for SQLModel models.
    """

    def __init__(self, model: type[SQLModel], *, session: AsyncSession | None = None, auto_commit: bool = True) -> None:
        """
        Initialize the BaseSQLModelCRUD with a SQLModel.

        Args:
            model (type[SQLModel]): The SQLModel class for the CRUD operations.
            session (AsyncSession | None): The SQLAlchemy session used for the CRUD operations.
            auto_commit (bool): Whether to automatically commit the changes.
        """

        self._model = model
        self._session = session
        self.auto_commit = auto_commit

    @property
    def model(self) -> type[SQLModel]:
        """
        Get the current model class.

        Returns:
            type[SQLModel]: The model class being used in the CRUD operations.
        """

        return self._model

    @property
    def session(self) -> AsyncSession:
        """
        Get Global session.

        Returns:
            AsyncSession: SQLAlchemy async session.

        Raises:
            RuntimeError: If the session is not initialized.
        """
        if self._session is None:
            raise RuntimeError("Session is not initialized.")
        return self._session

    async def commit(self, auto_commit: bool = True) -> None:
        """
        Commit the current transaction to the database.

        Args:
            auto_commit (bool): If True, automatically commit the transaction.
                If False, you need to commit manually after calling this method.
                Defaults to True.
        """
        auto_commit = auto_commit or self.auto_commit
        if auto_commit:
            await self.session.commit()

    @overload
    async def get(
        self,
        _id: UUID,
        /,
        *,
        session: AsyncSession | None = None,
        nullable: Literal[False],
    ) -> SQLModel: ...

    @overload
    async def get(
        self,
        _id: UUID,
        /,
        *,
        session: AsyncSession | None = None,
        nullable: Literal[True],
    ) -> SQLModel | None: ...

    @overload
    async def get(
        self,
        _id: UUID,
        /,
        *,
        session: AsyncSession | None = None,
    ) -> SQLModel | None: ...

    async def get(
        self,
        _id: UUID,
        /,
        *,
        nullable: bool = True,
        session: AsyncSession | None = None,
    ) -> SQLModel | None:
        """Retrieve a single record from the database by its primary key.

        Args:
            _id (UUID): The primary key of the record to be retrieved.
            nullable (bool): If True, allows returning None when the record is not found.
                             If False, raises an exception when the record is not found.
                             Default is True.
            session (AsyncSession): SQLAlchemy async session.

        Returns:
            SQLModel: The retrieved record as an instance of the model if found, otherwise None.

        Raises:
            NotFoundException: If nullable is False and the record is not found in the database.
        """
        session = session or self.session
        statement = select(self.model).filter(col(self.model.id) == _id)
        result = await session.exec(statement)
        response = result.first()

        if not nullable and not response:
            raise NotFoundException(detail=f"{_id} not found.")

        return response

    @overload
    async def get_by_ids(
        self,
        ids: list[UUID],
        *,
        order_by: ColumnElement[Any] | Any | None = None,
        session: AsyncSession | None = None,
        serializer: type[_PydanticBaseModel],
    ) -> list[_PydanticBaseModel]: ...

    @overload
    async def get_by_ids(
        self,
        ids: list[UUID],
        *,
        order_by: ColumnElement[Any] | Any | None = None,
        session: AsyncSession | None = None,
        serializer: Literal[None] = None,
    ) -> list[SQLModel]: ...

    async def get_by_ids(
        self,
        ids: list[UUID],
        *,
        order_by: ColumnElement[Any] | Any | None = None,
        session: AsyncSession | None = None,
        serializer: type[_PydanticBaseModel] | None = None,
    ) -> list[SQLModel] | list[_PydanticBaseModel]:
        """
        Retrieve multiple records from the database by a list of primary keys.

        Args:
            ids (list[UUID]): List of primary keys to retrieve.
            order_by (ColumnElement[Any] | None): Optional column element to order the results.
            session (AsyncSession | None): SQLAlchemy async session.
            serializer (type[_PydanticBaseModel]): Optional Pydantic model class used to
             serialize ORM records into validated output.

        Returns:
            list[SQLModel]: A list of retrieved records, or an empty list if none are found.
        """
        session = session or self.session
        statement = select(self.model).filter(col(self.model.id).in_(ids))
        if order_by is not None:
            statement = statement.order_by(order_by)
        result = await session.exec(statement)
        response = cast(list[SQLModel], result.all())

        if serializer is not None:
            return [serializer.model_validate(item) for item in response]
        return response

    @overload
    async def get_all(
        self,
        *args: ColumnElement[Any],
        order_by: ColumnElement[Any] | Any | None = None,
        session: AsyncSession | None = None,
        serializer: type[_PydanticBaseModel],
    ) -> list[_PydanticBaseModel]: ...

    @overload
    async def get_all(
        self,
        *args: ColumnElement[Any],
        order_by: ColumnElement[Any] | Any | None = None,
        session: AsyncSession | None = None,
        serializer: Literal[None] = None,
    ) -> list[SQLModel]: ...

    async def get_all(
        self,
        *args: ColumnElement[Any],
        order_by: ColumnElement[Any] | Any | None = None,
        session: AsyncSession | None = None,
        serializer: type[_PydanticBaseModel] | None = None,
    ) -> list[SQLModel] | list[_PydanticBaseModel]:
        """
        Retrieve all records from the database, with optional filters.

        Args:
            args (list[ColumnElement[Any]]): Optional list of filters to apply to the query.
            order_by (ColumnElement[Any] | None): Optional column element to order the results.
            session (AsyncSession): SQLAlchemy async session.
            serializer (type[_PydanticBaseModel]): Optional Pydantic model class used to
             serialize ORM records into validated output.

        Returns:
            list[SQLModel]: A list of all records matching the filters.

        Examples:
            from sqlmodel import col
            await self.get_all(order_by=col(YourModel.id).desc())
        """
        session = session or self.session
        statement = select(self.model).filter(*args)
        if order_by is not None:
            statement = statement.order_by(order_by)
        result = await session.exec(statement)
        response = cast(list[SQLModel], result.all())

        if serializer is not None:
            return [serializer.model_validate(item) for item in response]
        return response

    async def get_count(
        self,
        *args: ColumnExpressionArgument[bool],
        session: AsyncSession | None = None,
    ) -> int:
        """
        Retrieve the count of records in the database, with optional filters.

        Args:
            args (list[ColumnExpressionArgument[bool]]): Optional list of filters to apply to the query.
            session (AsyncSession | None): SQLAlchemy async session.

        Returns:
            int: The total number of records matching the filters.
        """
        session = session or self.session
        statement = select(func.count()).select_from(self.model).filter(*args)
        response = await session.exec(statement)

        return response.one()

    @overload
    async def get_paginate(
        self,
        *args: ColumnExpressionArgument[bool],
        page: int = 1,
        size: int = 20,
        order_by: ColumnElement[Any] | Any | None = None,
        session: AsyncSession | None = None,
        serializer: type[_PydanticBaseModel],
    ) -> PaginatedResponse[_PydanticBaseModel]: ...

    @overload
    async def get_paginate(
        self,
        *args: ColumnExpressionArgument[bool],
        page: int = 1,
        size: int = 20,
        order_by: ColumnElement[Any] | Any | None = None,
        session: AsyncSession | None = None,
        serializer: Literal[None] = None,
    ) -> PaginatedResponse[SQLModel]: ...

    async def get_paginate(
        self,
        *args: ColumnExpressionArgument[bool],
        page: int = 1,
        size: int = 20,
        order_by: ColumnElement[Any] | Any | None = None,
        session: AsyncSession | None = None,
        serializer: type[_PydanticBaseModel] | None = None,
    ) -> PaginatedResponse[SQLModel] | PaginatedResponse[_PydanticBaseModel]:
        """
        Retrieve a paginated list of records from the database with optional filters and ordering.

        Args:
            args (list[ColumnExpressionArgument[bool]]): Optional list of filters to apply to the query.
            page (int): The page number to retrieve.
            size (int): The number of records per page.
            order_by (ColumnElement[Any] | None): Optional column element to order the results.
            session (AsyncSession | None): SQLAlchemy async session.
            serializer (type[_PydanticBaseModel]): Optional Pydantic model class used to
             serialize ORM records into validated output.

        Returns:
            PaginatedResponse[SQLModel]: A paginated response containing the records and metadata.
        """
        session = session or self.session
        statement = select(self.model).filter(*args).offset((page - 1) * size).limit(size)

        if order_by is not None:
            statement = statement.order_by(order_by)

        result = await session.exec(statement)
        response = cast(list[SQLModel], result.all() or [])
        total = await self.get_count(*args, session=session)

        if serializer is not None:
            return PaginatedResponse(
                records=[serializer.model_validate(item) for item in response],
                total=total,
                page=page,
                page_size=size,
            )

        return PaginatedResponse(records=response, total=total, page=page, page_size=size)

    async def create(
        self,
        create_in: CreateSchema | SQLModel | dict[str, Any],
        *,
        validate: bool = True,
        session: AsyncSession | None = None,
        auto_commit: bool = False,
    ) -> SQLModel:
        """
        Create a new record in the database.

        Args:
            create_in (UpdateSchemaType | SQLModel | dict[str, Any]): Data to create the new record.
                Can be a Pydantic schema, SQLModel instance, or raw dictionary.
            validate (bool): Whether to validate input data before creation. Defaults to True.
            session (AsyncSession | None): SQLAlchemy async session for database operations.
            auto_commit(bool): Whether to automatically commit the changes. Defaults to False.

        Returns:
            SQLModel: The newly created model instance.

        Raises:
            ExistsException: If a record with conflicting unique constraints already exists.
            TypeError: If validation fails and validate=True.
        """
        session = session or self.session
        if not validate:
            if not isinstance(create_in, self.model):
                raise TypeError(f"Expected type {type(self.model)} for 'create_in', but got {type(create_in)}.")
        else:
            create_in = self.model.model_validate(create_in)

        try:
            session.add(create_in)
            await session.flush()

            await self.commit(auto_commit=auto_commit)
            await session.refresh(create_in)
        except IntegrityError:
            await session.rollback()
            raise ExistsException()

        return create_in

    async def create_all(
        self,
        create_in: Sequence[CreateSchema | SQLModel | dict],
        *,
        session: AsyncSession | None = None,
        auto_commit: bool = False,
    ) -> None:
        """
        Asynchronously create multiple records in the database.

        This method accepts a list of data (either as Pydantic schemas or SQLModel instances) and creates
        corresponding records in the database. The records will be validated using the model's schema
        before being added to the session.

        Args:
            create_in (Sequence[CreateSchema | SQLModel | dict]): A list of data used to create the new records.
                Each item can be a Pydantic schema or an SQLModel instance, and it will be validated
                before insertion.
            session (AsyncSession | None): An optional SQLAlchemy `AsyncSession` instance used to
                manage database transactions. If not provided, the method will use the default session.
            auto_commit(bool): Whether to automatically commit the changes. Defaults to False.

        Raises:
            ExistsException: If a record with conflicting unique constraints (e.g., duplicate entries)
                already exists in the database, the operation will raise an `ExistsException`.
        """
        session = session or self.session
        create_in = [self.model.model_validate(create_item) for create_item in create_in]

        try:
            session.add_all(create_in)
            await session.flush()

            await self.commit(auto_commit=auto_commit)
        except IntegrityError:
            await session.rollback()
            raise ExistsException()

    async def update(
        self,
        current_model: SQLModel,
        update_in: UpdateSchema | SQLModel | dict[str, Any],
        *,
        session: AsyncSession | None = None,
        auto_commit: bool = False,
    ) -> SQLModel:
        """
        Update an existing model instance with new data.

        Args:
            current_model (SQLModel): The existing model instance to update.
            update_in (UpdateSchemaType | SQLModel | dict[str, Any]): Update data. Can be schema, model, or dict.
                Only set fields will be updated.
            session (AsyncSession | None): SQLAlchemy async session.
            auto_commit(bool): Whether to automatically commit the changes. Defaults to False.

        Returns:
            SQLModel: The updated model instance.

        Note:
            Uses partial update - only fields explicitly set in update_in will be modified.
            None values will be treated as explicit updates unless filtered upstream.
        """
        session = session or self.session
        if not isinstance(update_in, dict):
            update_in = update_in.serializable_dict(exclude_unset=True, by_alias=False)

        for field, value in update_in.items():
            setattr(current_model, field, value)

        response = await self.create(current_model, validate=False, session=session, auto_commit=auto_commit)
        return response

    async def update_by_id(
        self,
        _id: UUID,
        /,
        update_in: UpdateSchema | dict[str, Any],
        *,
        session: AsyncSession | None = None,
        auto_commit: bool = False,
    ) -> SQLModel:
        """
        Update a record by its primary key.

        Args:
            _id (UUID): Primary key of the record to update.
            update_in (UpdateSchema | dict[str, Any]): Update data.
            session (AsyncSession | None): SQLAlchemy async session.
            auto_commit(bool): Whether to automatically commit the changes. Defaults to False.

        Returns:
            SQLModel: The updated model instance.

        Raises:
            NotFoundException: If no record exists with the specified ID.
        """
        session = session or self.session
        response = await self.get(_id, nullable=False, session=session)
        return await self.update(response, update_in, session=session, auto_commit=auto_commit)

    async def update_all(
        self, update_in: list[dict[str, Any]], *, session: AsyncSession | None = None, auto_commit: bool = False
    ) -> None:
        """
        Update a record by its primary key.

        Args:
            update_in (list[dict[str, Any]]): Update data.
            session (AsyncSession | None): SQLAlchemy async session.
            auto_commit(bool): Whether to automatically commit the changes. Defaults to False.

        Raises:
            ValueError: If any item is missing an 'id'.
            NotFoundException: If no record exists with the specified ID.
        """
        session = session or self.session
        try:
            for index, update_info in enumerate(update_in):
                _id = update_info.pop("id", None)
                if not _id:
                    raise ValueError(f"[index={index}] Missing 'id' in update payload.")

                statement = update(self.model).where(col(self.model.id) == _id).values(**update_info)
                result = await session.exec(statement)  # type: ignore
                if result.rowcount == 0:
                    raise NotFoundException(detail=f"[index={index}] ID '{_id}' not found.")

            await self.commit(auto_commit=auto_commit)

        except SQLAlchemyError as e:
            await session.rollback()
            raise RuntimeError("Database error during batch update.") from e

    async def delete(self, _id: UUID, /, *, session: AsyncSession | None = None, auto_commit: bool = False) -> SQLModel:
        """
        Delete a record from the database by its primary key.

        Args:
            _id (UUID): The primary key of the record to delete.
            session (AsyncSession | None): SQLAlchemy session.
            auto_commit(bool): Whether to automatically commit the changes. Defaults to False.

        Returns:
            SQLModel: The deleted record.

        Raises:
            NotFoundException: If the record with the specified primary key does not exist.
        """
        session = session or self.session
        response = await self.get(_id, nullable=False, session=session)
        await session.delete(response)
        await self.commit(auto_commit=auto_commit)
        return response

    async def delete_all(
        self, ids: list[UUID], /, *, session: AsyncSession | None = None, auto_commit: bool = True
    ) -> None:
        """
        Asynchronously delete multiple records from the database by their primary keys.

        This method will delete all records in the database that match the provided list of primary keys (`ids`).

        Args:
            ids (list[UUID]): A list of primary keys (UUIDs) of the records to delete.
            session (AsyncSession | None): An optional SQLAlchemy `AsyncSession`
            auto_commit(bool): Whether to automatically commit the changes. Defaults to False.
        """
        session = session or self.session
        statement = delete(self.model).filter(col(self.model.id).in_(ids))
        await session.exec(statement)  # type: ignore
        await self.commit(auto_commit=auto_commit)


class BaseBeanieCRUD(Generic[Document, CreateSchema, UpdateSchema]):
    """
    Base class for MongoDB CRUD operations using Beanie.

    This class provides generic CRUD operations for Beanie Document models.
    """

    def __init__(self, model: type[Document]) -> None:
        """
        Initializes the CRUD instance with the given model.

        Args:
            model (Type[Document]): The Beanie document model.
        """

        self._model = model

    @property
    def model(self) -> type[Document]:
        """
        Returns the document model associated with this CRUD instance.

        Returns:
            Type[Document]: The document model.
        """

        return self._model

    @overload
    async def get(
        self,
        _id: PydanticObjectId,
        /,
        *,
        nullable: Literal[False],
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document: ...

    @overload
    async def get(
        self,
        _id: PydanticObjectId,
        /,
        *,
        nullable: Literal[True],
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document | None: ...

    @overload
    async def get(
        self,
        _id: PydanticObjectId,
        /,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document | None: ...

    async def get(
        self,
        _id: PydanticObjectId,
        /,
        *,
        nullable: bool = True,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document | None:
        """
        Retrieves a document by its ID.

        Args:
            _id (PydanticObjectId): The document ID.
            nullable (bool): Whether to allow a None response. Defaults to True.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            Document | None: The retrieved document or None if not found.

        Raises:
            NotFoundException: If the document is not found and nullable is False.
        """

        response = await self.model.get(document_id=_id, session=session)

        if not nullable and not response:
            raise NotFoundException(detail=f"{_id} not found.")

        return response

    async def get_by_ids(
        self,
        ids: list[PydanticObjectId],
        /,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Document]:
        """
        Retrieves multiple documents by a list of IDs.

        Args:
            ids (list[Any]): List of document IDs.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            list[Document]: A list of retrieved documents.
        """
        response = await self.model.find(In(self.model.id, ids), session=session).to_list()
        return response

    async def get_all(
        self,
        *args: dict[str, Any] | bool,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Document]:
        """
        Retrieves all documents matching the given filters.

        Args:
            *args (dict[str, Any] | bool): Query filters.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            list[Document]: A list of matching documents.
        """

        response = await self.model.find(*args, session=session).to_list()
        return response

    async def get_count(
        self,
        *args: dict[str, Any] | bool,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """
        Counts the number of documents matching the given filters.

        Args:
            *args (dict[str, Any] | bool): Query filters.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            int: The count of matching documents.
        """

        response = await self.model.find(*args, session=session).count()
        return response

    async def get_paginate(
        self,
        *args: dict[str, Any] | bool,
        page: int = 1,
        size: int = 20,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
    ) -> PaginatedResponse[Document]:
        """
        Retrieves paginated results for documents matching the given filters.

        Args:
            *args (dict[str, Any] | bool): Query filters.
            page (int): Page number. Defaults to 1.
            size (int): Page size. Defaults to 20.
            order_by (str | tuple[str, int] | list[tuple[str, int]] | None): Sorting order. Defaults to None.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            dict: Paginated response containing records, total count, page, and page size.
        """

        result = self.model.find(*args, session=session).skip((page - 1) * size).limit(size)

        if order_by is not None:
            result.sort(*order_by)

        response = await result.to_list()
        total = await self.get_count(*args, session=session)

        return PaginatedResponse(records=response, total=total, page=page, page_size=size)

    async def create(
        self,
        create_in: CreateSchema | Document | dict[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document:
        """
        Creates a new document in the collection.

        Args:
            create_in (CreateSchema | Document | dict[str, Any]): The document to be created.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            Document: The created document.
        """
        response = self.model.model_validate(create_in)
        await response.create(session=session)

        return response

    @staticmethod
    async def update(
        current_model: Document,
        update_in: UpdateSchema | dict[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document:
        """
        Updates an existing document.

        Args:
            current_model (Document): The document to be updated.
            update_in (UpdateSchema | dict[str, Any]): The update data.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            Document: The updated document.
        """

        if not isinstance(update_in, dict):
            update_in = update_in.serializable_dict(exclude_unset=True)

        for field, value in update_in.items():
            setattr(current_model, field, value)

        await current_model.replace(session=session)  # type: ignore

        return current_model

    async def update_by_id(
        self,
        _id: PydanticObjectId,
        /,
        *,
        update_in: UpdateSchema | dict[str, Any],
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document:
        """
        Updates a document by its ID.

        Args:
            _id (PydanticObjectId): The document ID.
            update_in (UpdateSchema | dict[str, Any]): The update data.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            Document: The updated document.
        """

        update_model = await self.get(_id, nullable=False)
        return await self.update(update_model, update_in, session=session)

    async def delete(
        self,
        _id: PydanticObjectId,
        /,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document:
        """
        Deletes a document by its ID.

        Args:
            _id (PydanticObjectId): The document ID.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            Document: The deleted document.
        """

        update_model = await self.get(_id, nullable=False, session=session)
        await update_model.delete(session=session)  # type: ignore
        return update_model
