"""
Celery Periodic Task Models.

Author  : Coke
Date    : 2025-04-10
"""

from abc import abstractmethod
from datetime import timedelta
from enum import Enum
from typing import Any
from uuid import UUID

from celery.schedules import crontab as Crontab
from celery.schedules import schedule as Schedule
from celery.schedules import solar as Solar
from pydantic import BaseModel


class Period(Enum):
    """datetime.timedelta kwargs enum."""

    WEEKS = "weeks"
    DAYS = "days"
    HOURS = "hours"
    MINUTES = "minutes"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"


class SolarEvent(Enum):
    """Celery schedules solar events."""

    DAWN_ASTRONOMICAL = "dawn_astronomical"
    DAWN_NAUTICAL = "dawn_nautical"
    DAWN_CIVIL = "dawn_civil"
    SUNRISE = "sunrise"
    SOLAR_NOON = "solar_noon"
    SUNSET = "sunset"
    DUSK_CIVIL = "dusk_civil"
    DUSK_NAUTICAL = "dusk_nautical"
    DUSK_ASTRONOMICAL = "dusk_astronomical"


class BaseSchedule:
    """
    Base schedule model.

    To improve code type inference in IDEs such as VSCode or PyCharm,
    custom scheduler classes that inherit from Scheduler should explicitly implement the schedule property.
    """

    id: Any

    @property
    @abstractmethod
    def schedule(self) -> Any: ...


class IntervalSchedule(BaseSchedule):
    """Celery Interval Schedule model."""

    every: int
    period: Period

    @property
    def schedule(self) -> Schedule:
        return Schedule(
            timedelta(**{self.period.value: self.every}),
        )


class CrontabSchedule(BaseSchedule):
    """Celery Crontab Schedule model."""

    minute: str = "*"
    hour: str = "*"
    day_of_week: str = "*"
    day_of_month: str = "*"
    month_of_year: str = "*"

    @property
    def schedule(self) -> Crontab:
        return Crontab(
            minute=self.minute,
            hour=self.hour,
            day_of_week=self.day_of_week,
            day_of_month=self.day_of_month,
            month_of_year=self.month_of_year,
        )


class SolarSchedule(BaseSchedule):
    """Celery Solar Schedule model."""

    event: SolarEvent
    latitude: int
    longitude: int

    @property
    def schedule(self) -> Solar:
        return Solar(
            event=self.event.value,
            lat=self.latitude,
            lon=self.longitude,
        )


class TaskType(Enum):
    """Celery periodic task type enum."""

    INTERVAL = ("interval", IntervalSchedule)
    CRONTAB = ("crontab", CrontabSchedule)
    SOLAR = ("solar", SolarSchedule)

    def __init__(self, value: str, model: type[BaseSchedule]):
        self._value_ = value
        self._model_ = model

    @property
    def model(self) -> type[BaseSchedule]:
        return self._model_


class RetryPolicy(BaseModel):
    """
    Represents the retry policy for a task, based on Celery's retry configuration.

    Equivalent to Celery's beat retry_policy options:
        app = Celery("celery_app", broker=REDIS_URL, backend=REDIS_URL)
        app.conf.update({
            "beat_schedule": {
                "test_beat_task": {
                    "task": "src.queues.tasks.tasks.test_celery",
                    "schedule": 10,
                    "options": {
                        "retry_policy": `RetryPolicy`
                    }
                }
            }
        })
    """

    max_retries: int | None = None
    interval_start: int | None = None
    interval_step: int | None = None
    interval_max: int | None = None


class Options(BaseModel):
    """
    Options for configuring Celery task scheduling, similar to Celery's beat options.

    Equivalent to Celery's beat options:
        app = Celery("celery_app", broker=REDIS_URL, backend=REDIS_URL)
        app.conf.update({
            "beat_schedule": {
                "test_beat_task": {
                    "task": "src.queues.tasks.tasks.test_celery",
                    "schedule": 10,
                    "options": `Options`
                }
            }
        })
    """

    queue: str | None = None
    priority: int | None = None
    retry: bool = False
    expires: int | None = None
    task_id: str | None = None
    retry_policy: RetryPolicy


class PeriodicTask:
    """Celery Periodic Task Model."""

    name: str
    enabled: bool = True
    description: str = ""

    task: str
    task_type: TaskType
    schedule_id: UUID
    args: list[Any] | None
    kwargs: dict[str, Any] | None
    options: Options | None
