"""
Database Model Base Class with Timestamp Support.

Author : Coke
Date   : 2025-03-24
"""

from datetime import datetime
from uuid import UUID

from beanie import Document as _Document
from beanie import Replace, before_event
from pydantic import Field as PydanticField
from pydantic import field_serializer
from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel

from src.schemas.base import BaseModel
from src.utils.date import convert_datetime_to_gmt
from src.utils.uuid7 import uuid7


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
        description="Unique ID",
    )
    create_time: datetime = Field(default_factory=datetime.now, description="Creation time")
    update_time: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        description="Update time",
    )


# TODO: update base document by sqlmodel and add counter.
class Document(_Document):
    """
    Base Document class that combines Pydantic and Beanie functionality.

    Provides common fields and serialization for database models.
    """

    create_time: datetime = PydanticField(default_factory=datetime.now, examples=["2024-07-31 16:07:34"])
    update_time: datetime = PydanticField(default_factory=datetime.now, examples=["2024-07-31 16:07:34"])

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
