"""
Base model schemas.

This module defines the base model schemas used in the application.

Author : Coke
Date   : 2025-03-24
"""

from fastapi.encoders import jsonable_encoder
from pydantic import AliasGenerator, ConfigDict
from pydantic import BaseModel as _BaseModel
from pydantic.alias_generators import to_camel


class BaseModel(_BaseModel):
    """Base schemas."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_camel,
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),  # Use camel case for field names and aliases.
        populate_by_name=True,  # Allow populating fields by both name and alias.
    )

    def serializable_dict(self, by_alias=True) -> dict:
        """
        Convert the object into a JSON-serializable format and use aliases.

        This method ensures that the model can be easily converted to a dictionary
        that is compatible with JSON serialization, using field aliases if specified.

        Examples:
            class MyModel(BaseModel):
                page_size: int

            model = MyModel(pageSize=1)
            model.serializable_dict()
            >> {"pageSize": 1}

        Args:
            by_alias (bool): If True, uses field aliases in the output dictionary.
                            If False, uses field names.

        Returns:
            dict: A JSON-serializable dictionary representation of the model.
        """
        default_dict = self.model_dump(by_alias=by_alias)

        return jsonable_encoder(default_dict)
