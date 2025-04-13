"""
Celery scheduler.

Author  : Coke
Date    : 2025-04-10
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from celery import Celery
from celery.beat import ScheduleEntry as _ScheduleEntry
from celery.beat import Scheduler as _Scheduler
from kombu import Producer
from sqlmodel import select

from src.core.database import get_sync_session
from src.queues.models import PeriodicTask


class ScheduleEntry(_ScheduleEntry):
    """Custom Scheduler."""


class DatabaseScheduler(_Scheduler):
    """Custom Scheduler."""

    Entry = ScheduleEntry
    _store: dict[str, ScheduleEntry] = {}
    refresh_interval: float
    last_updated: datetime

    def __init__(
        self,
        app: Celery,
        *,
        refresh_interval: float | None = None,
        schedule: dict[str, ScheduleEntry] | None = None,
        max_interval: int | None = None,
        producer: type[Producer] | None = None,
        lazy: bool = False,
        sync_every_tasks: int | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        super().__init__(
            app=app,
            schedule=schedule,
            max_interval=max_interval,
            Producer=producer,
            lazy=lazy,
            sync_every_tasks=sync_every_tasks,
            **kwargs,
        )
        self.refresh_interval = refresh_interval or self.app.conf.get("refresh_interval") or 60
        self.last_updated = datetime.now(UTC)

    def _database_schedule(self) -> dict[str, ScheduleEntry]:
        """
        Fetches enabled periodic tasks from the database and returns them as a dictionary.

        Returns:
            dict[str, ScheduleEntry]
        """
        session = next(get_sync_session())
        tasks: list[PeriodicTask] = session.exec(
            select(PeriodicTask).where(PeriodicTask.enabled.is_(True))  # type: ignore
        ).all()

        celery_beat = {}
        for task in tasks:
            schedule_info = session.exec(
                select(task.task_type.model).where(task.task_type.model.id == task.schedule_id)  # type: ignore
            ).first()
            if schedule_info:
                celery_beat[task.name] = ScheduleEntry(
                    name=task.name,
                    task=task.task,
                    schedule=schedule_info.schedule,
                    args=task.args,
                    kwargs=task.kwargs,
                    options=task.options,
                )

        # Merge the configuration tasks and database tasks, with the configuration tasks taking higher priority.
        celery_beat.update(self.app.conf.beat_schedule)
        return celery_beat

    def setup_schedule(self) -> None:
        """Merges database tasks and config tasks, then installs default entries."""
        schedule = self._database_schedule()
        self.merge_inplace(schedule)
        self.install_default_entries(self._store)

    def get_schedule(self) -> dict[str, ScheduleEntry]:
        """Get schedule info."""
        return self._store

    def set_schedule(self, schedule: dict[str, ScheduleEntry]) -> None:
        """Set schedule info."""
        self._store = schedule

    def sync(self) -> None:
        """Synchronizes the in-memory schedule data to database."""
        # TODO: add sync database.
        super().sync()

    def close(self) -> None:
        """Closes the scheduler and clears the stored tasks."""
        super().close()
        self._store.clear()

    schedule = property(get_schedule, set_schedule)  # type: ignore

    def tick(self, *args: Any, **kwargs: Any) -> None:
        """
        Called on each scheduler heartbeat to refresh periodic tasks periodically.

        If the current time exceeds the last update time by more than
        `refresh_interval` seconds, reloads and merges the latest schedule
        from the database and config to keep tasks up-to-date.

        Then calls the parent class's tick method to continue normal scheduling.

        Args:
            *args (Any): Positional arguments passed to the parent tick method.
            **kwargs (Any): Keyword arguments passed to the parent tick method.
        """

        now = datetime.now(UTC)
        if (now - self.last_updated) > timedelta(seconds=self.refresh_interval):
            # TODO: The current implementation updates all tasks,
            #  but it should only update tasks that already exist in the database.
            self.setup_schedule()
            self.last_updated = now

        super().tick(*args, **kwargs)
