"""
schedule file.

Description.

Author : Coke
Date   : 2025-05-12
"""

from typing import Any

from sqlmodel import JSON, Column, Field

from src.models.base import SQLModel
from src.queues.models import CrontabSchedule as _CrontabSchedule
from src.queues.models import IntervalSchedule as _IntervalSchedule
from src.queues.models import Options
from src.queues.models import PeriodicTask as _PeriodicTask
from src.queues.models import SolarSchedule as _SolarSchedule


class IntervalSchedule(_IntervalSchedule, SQLModel, table=True):
    """Celery Interval Schedule sqlmodel model."""

    __tablename__ = "celery_interval_schedule"


class CrontabSchedule(_CrontabSchedule, SQLModel, table=True):
    """Celery Interval Schedule sqlmodel model."""

    __tablename__ = "celery_crontab_schedule"


class SolarSchedule(_SolarSchedule, SQLModel, table=True):
    """Celery Interval Schedule sqlmodel model."""

    __tablename__ = "celery_solar_schedule"


class PeriodicTask(_PeriodicTask, SQLModel, table=True):
    """Celery Periodic Task sqlmodel Model."""

    __tablename__ = "celery_periodic_task"

    args: list[Any] = Field([], sa_column=Column(JSON))
    kwargs: dict[str, Any] = Field({}, sa_column=Column(JSON))
    options: Options | None = Field(None, sa_column=Column(JSON))
