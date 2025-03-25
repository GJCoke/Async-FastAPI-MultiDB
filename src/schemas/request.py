"""
Request model schemas.

Author : Coke
Date   : 2025-03-24
"""

from uuid import UUID

from pydantic import Field

from .base import BaseModel


class BaseRequest(BaseModel):
    """Base request model."""


class PaginatedRequest(BaseRequest):
    """Unified paginated request."""

    page: int = Field(..., description="current page number.")
    page_size: int = Field(..., description="number of items per page.")


class SearchRequest(BaseRequest):
    """Unified search request."""

    keyword: str = Field(..., description="search keyword.")


class DeleteRequest(BaseRequest):
    """Unified delete request."""

    id: UUID = Field(..., description="item id to delete.")


class DetailsRequest(BaseRequest):
    """Unified details request."""

    id: UUID = Field(..., description="item id to retrieve details.")


class BatchRequest(BaseRequest):
    """Unified batch request."""

    ids: list[UUID] = Field(..., description="list of item ids.")
