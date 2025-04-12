"""
Celery Task.

Adds support for async def functions by converting asynchronous.

Author : Coke
Date   : 2025-04-12
"""

import asyncio
import warnings
from datetime import datetime, timedelta
from typing import Any, Iterable

from celery import Task as _Task

# noinspection PyProtectedMember
from celery._state import _task_stack
from celery.app.routes import Router
from celery.canvas import Signature
from celery.result import AsyncResult
from kombu import Connection, Producer
from typing_extensions import Annotated, Doc


class Task(_Task):
    """
    Custom Celery Task that supports running asynchronous (async def) tasks.

    This task class overrides the default `__call__` method to detect whether
    the result of `run()` is a coroutine. If it is, the coroutine is executed
    within an appropriate event loop context.
    """

    def apply_async(
        self,
        args: Annotated[
            tuple[Any] | None,
            Doc(
                """
                Positional arguments for the task (list or tuple).
                """
            ),
        ] = None,
        kwargs: Annotated[
            dict[str, Any] | None,
            Doc(
                """
                Keyword arguments for the task (dict).
                """
            ),
        ] = None,
        countdown: Annotated[
            int | float | None,
            Doc(
                """
                Number of seconds to delay execution.
                """
            ),
        ] = None,
        eta: Annotated[
            datetime | None,
            Doc(
                """
                Exact time to execute the task (as a datetime object).
                """
            ),
        ] = None,
        expires: Annotated[
            int | float | datetime | None,
            Doc(
                """
                Expiration time or seconds until the task expires.
                """
            ),
        ] = None,
        task_id: Annotated[
            str | None,
            Doc(
                """
                Custom task ID; if not set, Celery generates one automatically.
                """
            ),
        ] = None,
        retry: Annotated[
            bool,
            Doc(
                """
                Whether the task should be retried on failure.
                """
            ),
        ] = False,
        retry_policy: Annotated[
            dict[str, Any] | None,
            Doc(
                """
                Dictionary defining the retry behavior (max retries, intervals, etc.).
                """
            ),
        ] = None,
        queue: Annotated[
            str | None,
            Doc(
                """
                Name of the queue to send the task to.
                """
            ),
        ] = None,
        priority: Annotated[
            int,
            Doc(
                """
                Task priority (0 = highest, 255 = lowest).
                """
            ),
        ] = 0,
        producer: Annotated[
            Producer | None,
            Doc(
                """
                Custom kombu.Producer instance used to publish the task message.

                If provided, this producer will be used instead of Celery's default
                message publisher. This allows for fine-grained control over the message
                publishing process, such as customizing delivery options, using a specific
                channel or connection, or reusing existing connections to improve performance.
                """
            ),
        ] = None,
        connection: Annotated[
            Connection | None,
            Doc(
                """
                Custom connection to message broker.
                """
            ),
        ] = None,
        link: Annotated[
            Signature | Iterable[Signature] | None,
            Doc(
                """
                A task (or list of tasks) to call if this task succeeds.
                """
            ),
        ] = None,
        link_error: Annotated[
            Signature | Iterable[Signature] | None,
            Doc(
                """
                A task (or list of tasks) to call if this task fails.
                """
            ),
        ] = None,
        chain: Annotated[
            Signature | list[Signature] | None,
            Doc(
                """
                Chain of follow-up tasks.
                """
            ),
        ] = None,
        shadow: Annotated[
            str | None,
            Doc(
                """
                Use the task's original name (i.e., the function name).
                """
            ),
        ] = None,
        router: Annotated[
            Router | None,
            Doc(
                """
                Custom task router.
                """
            ),
        ] = None,
        add_to_parent: Annotated[
            bool,
            Doc(
                """
                Add to parent task’s group.
                """
            ),
        ] = True,
        group_id: Annotated[
            str | None,
            Doc(
                """
                Group ID.
                """
            ),
        ] = None,
        group_index: Annotated[
            int,
            Doc(
                """
                Index in task group.
                """
            ),
        ] = 0,
        reply_to: Annotated[
            str | None,
            Doc(
                """
                Queue name to reply to.
                """
            ),
        ] = None,
        time_limit: Annotated[
            int | None,
            Doc(
                """
                Hard time limit.
                """
            ),
        ] = None,
        soft_time_limit: Annotated[
            int | None,
            Doc(
                """
                Soft time limit.
                """
            ),
        ] = None,
        root_id: Annotated[
            str | None,
            Doc(
                """
                Root task ID.
                """
            ),
        ] = None,
        parent_id: Annotated[
            str | None,
            Doc(
                """
                Parent task ID.
                """
            ),
        ] = None,
        route_name: Annotated[
            str | None,
            Doc(
                """
                Route name.
                """
            ),
        ] = None,
        ignore_warning: Annotated[
            bool,
            Doc(
                """
                `Custom parameter`: Whether to ignore warning messages. Default value False.
                """
            ),
        ] = False,
        **options: Annotated[
            dict[str, Any],
            Doc(
                """
                Celery options.
                """
            ),
        ],
    ) -> AsyncResult:
        # Added full type annotations for Celery's apply_async method parameters,
        # enhancing code readability and IDE support.
        # For more parameter types, please refer to the official Celery documentation.

        if not ignore_warning:
            if (
                countdown is not None
                and countdown > 3600
                or eta is not None
                and eta > datetime.now() + timedelta(hours=1)
            ):
                warnings.warn(
                    "The recommended maximum duration for countdown is no more than 1 hour. If a task needs to "
                    "be delayed for longer than that, it's advisable to use scheduled task mechanisms such as "
                    "Celery Beat to ensure better reliability and resource efficiency."
                    "You can suppress this warning by setting the ignore_warning parameter to True.",
                    RuntimeWarning,
                )

        return super().apply_async(
            args=args,
            kwargs=kwargs,
            countdown=countdown,
            eta=eta,
            expires=expires,
            task_id=task_id,
            retry=retry,
            retry_policy=retry_policy,
            queue=queue,
            priority=priority,
            producer=producer,
            connection=connection,
            link=link,
            link_error=link_error,
            chain=chain,
            shadow=shadow,
            router=router,
            add_to_parent=add_to_parent,
            group_id=group_id,
            group_index=group_index,
            reply_to=reply_to,
            time_limit=time_limit,
            soft_time_limit=soft_time_limit,
            root_id=root_id,
            parent_id=parent_id,
            route_name=route_name,
            **options,
        )

    def __call__(self, *args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
        """
        Execute the task, with support for both sync and async run methods.

        If `run()` returns a coroutine, the method will attempt to run it using
        the current running event loop. If no loop is running, it will create
        and run a new one using `asyncio.run()`.

        Args:
            *args: Positional arguments passed to the task.
            **kwargs: Keyword arguments passed to the task.

        Returns:
            Any: The result of the task execution, either from the coroutine or regular function.

        Raises:
            Exception: Re-raises any exception that occurs during task execution
                       after calling `on_failure()`.
        """

        _task_stack.push(self)
        self.push_request(args=args, kwargs=kwargs)

        try:
            # Call the original run() method with provided arguments.
            result = self.run(*args, **kwargs)
            # Check if the result is a coroutine (i.e., async function).
            if asyncio.iscoroutine(result):
                try:
                    # Try to get the currently running event loop.
                    # If successful, execute the coroutine using run_until_complete.
                    loop = asyncio.get_running_loop()
                    return loop.run_until_complete(result)

                except RuntimeError:
                    # If no running event loop exists, start a new one with asyncio.run.
                    return asyncio.run(result)

            # If result is not a coroutine, return it directly
            return result

        finally:
            self.pop_request()
            _task_stack.pop()
