"""
Author  : Coke
Date    : 2025-04-24
"""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo


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


def get_current_utc_time() -> datetime:
    """Get current UTC time."""
    return datetime.now(UTC)
