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
from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel

from src.utils.uuid7 import uuid7


class SQLModel(_SQLModel):
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


class Document(_Document):
    """
    Base Document class that combines Pydantic and Beanie functionality.

    Provides common fields and serialization for database models.
    """

    create_time: datetime = PydanticField(default_factory=datetime.now, description="Creation time")
    update_time: datetime = PydanticField(default_factory=datetime.now, description="Update time")

    @before_event(Replace)
    def set_update_time(self) -> None:
        """
        Sets the update_time field to the current timestamp before saving the document.

        This method is triggered before the document is saved to the database,
        ensuring that the update_time field reflects the last modification time.
        """
        self.update_time = datetime.now()
