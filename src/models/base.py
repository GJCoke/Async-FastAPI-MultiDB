"""
Database Model Base Class with Timestamp Support.

Author : Coke
Date   : 2025-03-24
"""

from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from beanie import Document as _Document
from beanie import Replace, before_event
from pydantic import field_serializer
from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel

from src.schemas.base import BaseModel
from src.utils.uuid7 import uuid7


def convert_datetime_to_gmt(dt: datetime) -> str:
    """
    Convert datetime object to GMT timezone string representation.

    Args:
        dt: datetime object to convert (naive or aware)

    Returns:
        String formatted as '%Y-%m-%d %H:%M:%S' in GMT timezone
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class SQLModel(_SQLModel, BaseModel):  # type: ignore
    """
    Base SQLModel class that combines Pydantic and SQLAlchemy functionality.

    Inherits from both BaseModel (custom Pydantic model) and SQLModel (SQLAlchemy model).
    Provides common fields and serialization for database models.
    """

    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )
    create_time: datetime = Field(
        default_factory=datetime.now,
        schema_extra={"examples": ["2024-07-31 16:07:34"]},
    )
    update_time: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        schema_extra={"examples": ["2024-07-31 16:07:34"]},
    )

    @field_serializer("create_time", "update_time")
    def serialize_datetime(self, value: datetime) -> str:
        """
        Pydantic serializer for datetime fields.

        Converts datetime fields to GMT string format when serializing to JSON.

        Args:
            value: datetime value to serialize

        Returns:
            String representation of datetime in GMT
        """
        return convert_datetime_to_gmt(value)


class Document(_Document, BaseModel):
    """
    Base Document class that combines Pydantic and Beanie functionality.

    Inherits from both BaseModel (custom Pydantic model) and Document (Beanie model).
    Provides common fields and serialization for database models.
    """

    # TODO: find _id to id method.
    # id: PydanticObjectId = Field(
    #     alias="_id",
    #     nullable=False,
    #     primary_key=True,
    # )

    create_time: datetime = Field(
        default_factory=datetime.now,
        schema_extra={"examples": ["2024-07-31 16:07:34"]},
    )
    update_time: datetime = Field(
        default_factory=datetime.now,
        schema_extra={"examples": ["2024-07-31 16:07:34"]},
    )

    @before_event(Replace)
    def set_update_time(self) -> None:
        """
        Sets the update_time field to the current timestamp before saving the document.

        This method is triggered before the document is saved to the database,
        ensuring that the update_time field reflects the last modification time.
        """
        self.update_time = datetime.now()

    @field_serializer("create_time", "update_time")
    def serialize_datetime(self, value: datetime) -> str:
        """
        Pydantic serializer for datetime fields.

        Converts datetime fields to GMT string format when serializing to JSON.

        Args:
            value: datetime value to serialize

        Returns:
            String representation of datetime in GMT
        """
        return convert_datetime_to_gmt(value)
