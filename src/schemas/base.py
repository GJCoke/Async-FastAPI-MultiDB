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
from pydantic.main import IncEx


class BaseModel(_BaseModel):
    """Base schemas."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(alias=to_camel),  # Use camel case for field names and aliases.
        populate_by_name=True,  # Allow populating fields by both name and alias.
    )

    def serializable_dict(
        self,
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> dict:
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
            include (IncEx | None): Whitelist of fields to include in the output.
                Can be a set of field names, dictionary of {field: True}, or None to include all.

            exclude (IncEx | None): Blacklist of fields to exclude from the output.
                Same format as `include`. Takes precedence over `include`.

            by_alias (bool): If True, uses field aliases in the output dictionary.
                If False, uses the original field names.

            exclude_unset (bool): If True, excludes fields that weren't explicitly set,
                including fields with default values that weren't modified.

            exclude_defaults (bool): If True, excludes fields that are equal to their
                default values (even if they were explicitly set).

            exclude_none (bool): If True, excludes fields that have None values.

        Returns:
            dict: A JSON-serializable dictionary representation of the model.
        """
        default_dict = self.model_dump(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

        return jsonable_encoder(default_dict)
