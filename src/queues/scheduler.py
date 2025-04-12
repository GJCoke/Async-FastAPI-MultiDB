"""
Celery scheduler.

Author  : Coke
Date    : 2025-04-10
"""

from celery.beat import ScheduleEntry as _ScheduleEntry
from celery.beat import Scheduler as _Scheduler


class ScheduleEntry(_ScheduleEntry):
    """Custom Scheduler."""


class Scheduler(_Scheduler):
    """Custom Scheduler."""
