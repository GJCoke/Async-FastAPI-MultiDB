"""
Author  : Coke
Date    : 2025-04-10
"""

from datetime import timedelta
from enum import Enum

from celery.schedules import schedule as Schedule
from pydantic import Field

from src.models.base import SQLModel


class Period(Enum):
    WEEKS = "weeks"
    DAYS = "days"
    HOURS = "hours"
    MINUTES = "minutes"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"


class IntervalSchedule(SQLModel, table=True):
    __tablename__ = "celery_interval_schedule"

    every: int = Field(..., description="每多少单位时间执行一次")
    period: Period = Field(..., description="时间单位")

    @property
    def schedule(self) -> Schedule:
        return Schedule(
            timedelta(**{self.period.value: self.every}),
        )
