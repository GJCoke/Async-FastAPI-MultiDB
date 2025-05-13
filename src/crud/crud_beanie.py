"""
beanie file.

Description.

Author : Coke
Date   : 2025-05-13
"""

from typing import Any, Generic, Literal, Mapping, Sequence, TypeVar, overload

from beanie import PydanticObjectId, SortDirection
from beanie.operators import In
from motor.motor_asyncio import AsyncIOMotorClientSession
from pydantic import BaseModel as PydanticBaseModel
from pymongo import DeleteOne, UpdateOne

from src.core.exceptions import InvalidParameterError, NotFoundException
from src.models.base import Document as _Document
from src.schemas.base import BaseModel
from src.schemas.response import PaginatedResponse

Document = TypeVar("Document", bound=_Document)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)
_PydanticBaseModel = TypeVar("_PydanticBaseModel", bound=PydanticBaseModel)


def normalize_order(order_by: str | tuple[str, SortDirection]) -> tuple[str, SortDirection]:
    """
    Normalize the ordering field, converting 'id' to '_id', and ensuring
    a consistent (field, direction) tuple format.

    Args:
        order_by (str | tuple[str, SortDirection]): The ordering input, either a string
            representing the field name, or a tuple of (field, direction).

    Returns:
        tuple[str, SortDirection]: A normalized tuple representing the sort field and direction.
    """
    field, direction = (order_by, SortDirection.ASCENDING) if isinstance(order_by, str) else order_by
    if field == "id":
        field = "_id"
    return field, direction


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
        _id: PydanticObjectId | None,
        /,
        *,
        nullable: Literal[False],
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document: ...

    @overload
    async def get(
        self,
        _id: PydanticObjectId | None,
        /,
        *,
        nullable: Literal[True],
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document | None: ...

    @overload
    async def get(
        self,
        _id: PydanticObjectId | None,
        /,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document | None: ...

    async def get(
        self,
        _id: PydanticObjectId | None,
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

        if not _id:
            raise InvalidParameterError(param="_id")

        response = await self.model.get(document_id=_id, session=session)

        if not nullable and not response:
            raise NotFoundException(detail=f"{_id} not found.")

        return response

    @overload
    async def get_by_ids(
        self,
        ids: list[PydanticObjectId | None],
        *,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
        serializer: type[_PydanticBaseModel],
    ) -> list[_PydanticBaseModel]: ...

    @overload
    async def get_by_ids(
        self,
        ids: list[PydanticObjectId | None],
        *,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
        serializer: Literal[None] = None,
    ) -> list[Document]: ...

    async def get_by_ids(
        self,
        ids: list[PydanticObjectId | None],
        *,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
        serializer: type[_PydanticBaseModel] | None = None,
    ) -> list[Document] | list[_PydanticBaseModel]:
        """
        Retrieves multiple documents by a list of IDs.

        Args:
            ids (list[Any]): List of document IDs.
            order_by (str | tuple[str, int] | list[tuple[str, int]] | None): Sorting order. Defaults to None.
            session (AsyncIOMotorClientSession | None): Motor client async session.
            serializer (type[_PydanticBaseModel]): Optional Pydantic model class used to
             serialize ORM records into validated output.

        Returns:
            list[Document]: A list of retrieved documents.
        """
        if not ids:
            raise InvalidParameterError(param="ids")

        statement = self.model.find(In(self.model.id, ids), session=session)
        if order_by is not None:
            order_by_list = [order_by] if isinstance(order_by, (str, tuple)) else order_by
            sort_list = [normalize_order(item) for item in order_by_list]
            statement = statement.sort(*sort_list)

        response = await statement.to_list()
        if serializer is not None:
            return [serializer.model_validate(item) for item in response]
        return response

    @overload
    async def get_all(
        self,
        *args: Mapping[str, Any] | bool,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
        serializer: type[_PydanticBaseModel],
    ) -> list[_PydanticBaseModel]: ...

    @overload
    async def get_all(
        self,
        *args: Mapping[str, Any] | bool,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
        serializer: Literal[None] = None,
    ) -> list[Document]: ...

    async def get_all(
        self,
        *args: Mapping[str, Any] | bool,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
        serializer: type[_PydanticBaseModel] | None = None,
    ) -> list[Document] | list[_PydanticBaseModel]:
        """
        Retrieves all documents matching the given filters.

        Args:
            *args (dict[str, Any] | bool): Query filters.
            order_by (str | tuple[str, int] | list[tuple[str, int]] | None): Sorting order. Defaults to None.
            session (AsyncIOMotorClientSession | None): Motor client async session.
            serializer (type[_PydanticBaseModel]): Optional Pydantic model class used to
             serialize ORM records into validated output.

        Returns:
            list[Document]: A list of matching documents.
        """
        statement = self.model.find(*args, session=session)
        if order_by is not None:
            order_by_list = [order_by] if isinstance(order_by, (str, tuple)) else order_by
            sort_list = [normalize_order(item) for item in order_by_list]
            statement = statement.sort(*sort_list)

        response = await statement.to_list()
        if serializer is not None:
            return [serializer.model_validate(item) for item in response]
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

    @overload
    async def get_paginate(
        self,
        *args: dict[str, Any] | bool,
        page: int = 1,
        size: int = 20,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
        serializer: type[_PydanticBaseModel],
    ) -> PaginatedResponse[_PydanticBaseModel]: ...

    @overload
    async def get_paginate(
        self,
        *args: dict[str, Any] | bool,
        page: int = 1,
        size: int = 20,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
        serializer: Literal[None] = None,
    ) -> PaginatedResponse[Document]: ...

    async def get_paginate(
        self,
        *args: dict[str, Any] | bool,
        page: int = 1,
        size: int = 20,
        order_by: str | tuple[str, SortDirection] | list[tuple[str, SortDirection]] | None = None,
        session: AsyncIOMotorClientSession | None = None,
        serializer: type[_PydanticBaseModel] | None = None,
    ) -> PaginatedResponse[Document] | PaginatedResponse[_PydanticBaseModel]:
        """
        Retrieves paginated results for documents matching the given filters.

        Args:
            *args (dict[str, Any] | bool): Query filters.
            page (int): Page number. Defaults to 1.
            size (int): Page size. Defaults to 20.
            order_by (str | tuple[str, int] | list[tuple[str, int]] | None): Sorting order. Defaults to None.
            session (AsyncIOMotorClientSession | None): Motor client async session.
            serializer (type[_PydanticBaseModel]): Optional Pydantic model class used to
             serialize ORM records into validated output.

        Returns:
            dict: Paginated response containing records, total count, page, and page size.
        """

        statement = self.model.find(*args, session=session).skip((page - 1) * size).limit(size)
        if order_by is not None:
            order_by_list = [order_by] if isinstance(order_by, (str, tuple)) else order_by
            sort_list = [normalize_order(item) for item in order_by_list]
            statement = statement.sort(*sort_list)

        response = await statement.to_list()
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
        if not isinstance(create_in, dict):
            create_in = create_in.model_dump()
        create = self.model.model_validate(create_in)
        response = await create.create(session=session)
        return response

    async def create_all(
        self,
        creates_in: Sequence[CreateSchema | Document | dict[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """
        Create multiple documents in the database in a single batch operation.

        Args:
            creates_in (Sequence[CreateSchema | Document | dict[str, Any]]):
                A sequence of items to be inserted. Each item can be a Pydantic schema,
                a Document instance, or a raw dictionary.

            session (AsyncIOMotorClientSession | None):
                Optional MongoDB session for transactional support. Defaults to None.
        """
        if not creates_in:
            raise InvalidParameterError(param="creates_in")

        update_models = [
            self.model.model_validate(item if isinstance(item, dict) else item.model_dump()) for item in creates_in
        ]
        await self.model.insert_many(update_models, session=session)

    @staticmethod
    async def update(
        current_model: Document,
        update_in: UpdateSchema | Document | dict[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Document:
        """
        Updates an existing document.

        Args:
            current_model (Document): The document to be updated.
            update_in (UpdateSchema | Document | dict[str, Any]): The update data.
            session (AsyncIOMotorClientSession | None): Motor client async session.

        Returns:
            Document: The updated document.
        """

        if not isinstance(update_in, dict):
            update_in = update_in.model_dump(exclude_unset=True)

        for field, value in update_in.items():
            setattr(current_model, field, value)
        current_model = await current_model.replace(session=session)  # type: ignore
        return current_model

    async def update_by_id(
        self,
        _id: PydanticObjectId | None,
        /,
        update_in: UpdateSchema | dict[str, Any],
        *,
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
        if not _id:
            raise InvalidParameterError(param="_id")

        update_model = await self.get(_id, nullable=False)
        return await self.update(update_model, update_in, session=session)

    async def update_all(
        self,
        updates_in: list[dict[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """
        Perform bulk update operations on documents using MongoDB's bulk_write.

        Each item in `updates_in` must contain an "_id" key, which is used to match
        the document, and the rest of the keys will be used as fields to update.

        Args:
            updates_in (list[dict[str, Any]]): A list of dictionaries where each dictionary
                represents a document update. Must contain "_id" and update fields.
            session (AsyncIOMotorClientSession | None, optional): Optional MongoDB session
                for transactional support.

        Raises:
            ValueError: If any update dictionary does not contain the required "_id" key.
        """

        if not updates_in:
            raise InvalidParameterError(param="updates_in")

        statements = []
        for index, update_info in enumerate(updates_in):
            _id = update_info.pop("id", None) or update_info.pop("_id", None)
            if not _id:
                raise ValueError(f"[index={index}] Missing 'id' in update payload.")

            statements.append(UpdateOne({"_id": _id}, {"$set": update_info}))

        collection = self.model.get_motor_collection()
        await collection.bulk_write(statements, session=session)

    async def delete(
        self,
        _id: PydanticObjectId | None,
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

        if not _id:
            raise InvalidParameterError(param="_id")

        delete_model = await self.get(_id, nullable=False, session=session)
        await delete_model.delete(session=session)  # type: ignore
        return delete_model

    async def delete_all(
        self,
        ids: list[PydanticObjectId | None],
        /,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """
        Bulk delete documents by their id.

        Args:
            ids (Sequence[PydanticObjectId | None]): List of document ObjectIDs to delete.
            session (AsyncIOMotorClientSession, optional): MongoDB transaction session.
        """
        if not ids:
            raise InvalidParameterError(param="ids")

        statements = [DeleteOne({"_id": _id}) for _id in ids if _id is not None]
        collection = self.model.get_motor_collection()
        await collection.bulk_write(statements, session=session)
