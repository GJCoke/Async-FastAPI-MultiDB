"""
Celery scheduler.

Author  : Coke
Date    : 2025-04-10
"""

import asyncio
from abc import abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any, Coroutine, Sequence

from celery.beat import ScheduleEntry as _ScheduleEntry
from celery.beat import Scheduler as _Scheduler
from celery.utils.log import get_logger
from kombu import Producer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.queues.celery import Celery
from src.queues.models import PeriodicTask

logger = get_logger("celery.queues.scheduler")


class ScheduleEntry(_ScheduleEntry):
    """Custom Scheduler."""


class Scheduler(_Scheduler):
    """Custom Scheduler."""

    Entry = ScheduleEntry
    _store: dict[str, ScheduleEntry] = {}
    refresh_interval: float
    last_updated: datetime

    def __init__(
        self,
        app: Celery,
        *,
        refresh_interval: bool | float = False,
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
        self.refresh_interval = refresh_interval or self.app.conf.get("refresh_interval")
        logger.info(f"Synchronize database tasks every {self.refresh_interval} seconds.")
        self.last_updated = datetime.now(UTC)

    @abstractmethod
    def get_database_schedule(self) -> dict[str, ScheduleEntry] | Coroutine[Any, Any, dict[str, ScheduleEntry]]:
        return {}

    def _database_schedule(self) -> dict[str, ScheduleEntry]:
        """
        Retrieves and merges Celery beat schedule from the database and configuration.

        If the database schedule is an asynchronous coroutine, it is awaited
        appropriately. The resulting schedule is merged with the statically configured
        beat_schedule from the application config, where config tasks override database tasks.

        Returns:
            dict[str, ScheduleEntry]: A merged dictionary of scheduled tasks.
        """
        celery_beat = self.get_database_schedule()

        if asyncio.iscoroutine(celery_beat):
            loop = asyncio.get_event_loop()
            celery_beat = loop.run_until_complete(celery_beat)

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
        # TODO: if in tick update database schedule ? is it need threading ?
        if self.refresh_interval and (now - self.last_updated) > timedelta(seconds=self.refresh_interval):
            # TODO: The current implementation updates all tasks,
            #  but it should only update tasks that already exist in the database.
            self.setup_schedule()
            self.last_updated = now

        super().tick(*args, **kwargs)


class AsyncDatabaseScheduler(Scheduler):
    """Async Database Scheduler."""

    def __init__(self, app: Celery, **kwargs: Any) -> None:
        database_url = app.conf.get("database_url")
        if database_url is None:
            raise ValueError("Database URL must be configured.")
        async_engine = create_async_engine(database_url)
        self.AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
        super().__init__(app, **kwargs)

    async def get_database_schedule(self) -> dict[str, ScheduleEntry]:
        """
        Fetches enabled periodic tasks from the database and returns them as a dictionary.

        Returns:
            dict[str, ScheduleEntry]
        """
        async with self.AsyncSessionLocal() as session:
            _tasks = await session.exec(select(PeriodicTask).filter(col(PeriodicTask.enabled).is_(True)))
            tasks: Sequence[PeriodicTask] = _tasks.all()

            celery_beat = {}
            for task in tasks:
                _schedule_info = await session.exec(
                    select(task.task_type.model).filter(col(task.task_type.model.id) == task.schedule_id)
                )
                schedule_info = _schedule_info.first()
                if schedule_info:
                    celery_beat[task.name] = ScheduleEntry(
                        name=task.name,
                        task=task.task,
                        schedule=schedule_info.schedule,
                        args=task.args,
                        kwargs=task.kwargs,
                        options=task.options,
                    )

            logger.info(
                f"Database scheduled tasks({len(celery_beat)}): {', '.join([name for name in celery_beat.keys()])}"
            )
            return celery_beat
