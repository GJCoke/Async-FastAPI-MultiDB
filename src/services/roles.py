"""
Author  : Coke
Date    : 2025-04-30
"""

from sqlalchemy import ColumnElement
from sqlmodel import col, or_

from src.models import Role


def filter_role(status: bool | None, keyword: str) -> list[ColumnElement[bool]]:
    """
    Generate SQLAlchemy filter conditions for querying roles.

    Args:
        status (bool | None): Role status to filter by. If None, this filter is ignored.
        keyword (str): Keyword to search in role name or code.

    Returns:
        list[ColumnElement[bool]]: A list of SQLAlchemy filter expressions.
    """
    filter = []

    if status is not None:
        filter.append(col(Role.status) == status)

    if keyword:
        filter.append(or_(col(Role.name).like(f"%{keyword}%"), col(Role.code).like(f"%{keyword}%")))

    return filter
