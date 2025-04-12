"""
Celery.

Author  : Coke
Date    : 2025-04-10
"""

from typing import Any

from celery import Celery as _Celery
from typing_extensions import Annotated, Doc

from src.queues.task import Task

MINUTES = 60
HOURS = 60 * MINUTES
DAYS = 24 * HOURS
WEEKDAYS = 7 * DAYS


class Celery(_Celery):
    """
    Custom Celery.

    This code simply improves IDE type hints for Celery and adds support for async def functions
    by converting asynchronous functions into synchronous execution using asyncio.
    """

    def task(
        self,
        *args: Any,
        name: Annotated[
            str | None,
            Doc(
                """
                Every task must have a unique name.

                If no explicit name is provided the task decorator will generate one for you, and this
                name will be based on 1) the module the task is defined in, and 2) the name of the task function.

                Examples:
                    @app.task(name='sum-of-two-numbers')
                    def add(x, y):
                        return x + y

                    print(add.name) -> 'sum-of-two-numbers'
                """
            ),
        ] = None,
        base: Annotated[
            type[Task],
            Doc(
                """
                The base parameter is used to specify the base class for the task. By default,
                the base class for Celery tasks is celery.Task.
                By specifying base, you can define a custom base class for the task in order to implement special
                behaviors or modify the default behavior of the task.

                Examples:
                    import celery

                    class MyTask(celery.Task):

                        def on_failure(self, exc, task_id, args, kwargs, einfo):
                            print('{0!r} failed: {1!r}'.format(task_id, exc))

                    @app.task(base=MyTask)
                    def add(x, y):
                        raise KeyError()
                """
            ),
        ] = Task,
        bind: Annotated[
            bool,
            Doc(
                """
                `bind=True` makes the task a "bound task,"
                meaning the `run` method of the task will receive an additional self parameter,
                where `self` represents the current task instance. Through this instance,
                you can access various information about the task (such as task ID, retry mechanisms, etc.)
                and call methods of the task instance (like `self.retry()`).

                `bind=False` (the default value) means the task is not bound to the current task instance,
                and the `run` method will only receive the task's arguments,
                without access to the instance's properties and methods.

                Examples:
                    @app.task(bind=True)
                    def add(self: Task, x, y):
                        try:
                            return MyTask().run(x, y)
                        except TypeError:
                            self.retry()
                """
            ),
        ] = False,
        acks_late: Annotated[
            bool,
            Doc(
                """
                `acks_late=True`: This means that the acknowledgment will be sent after the task has been
                successfully completed.  In other words, Celery will not acknowledge the task as completed until
                the run method of the task finishes without errors.

                Use case: This is particularly useful if you want to ensure that tasks are not lost in case
                of worker crashes during task execution.  If the worker crashes before the task finishes,
                the task will be re-queued and retried by another worker.

                `acks_late=False` (default behavior): This means that the acknowledgment is sent as soon as
                the task is received by the worker, even before the task is actually executed.
                This could lead to tasks being lost if the worker crashes during execution,
                because Celery considers the task as successfully completed the moment it starts processing.

                Use case: This is useful in scenarios where you want tasks to be acknowledged
                immediately to avoid task retries, assuming the tasks are idempotent (safe to execute multiple times).

                Examples:
                    @app.task(acks_late=True)
                    def add(data):
                        if data == "error":
                            raise Exception("Something went wrong!")
                        return f"Processed {data}"
                """
            ),
        ] = False,
        max_retries: Annotated[
            int,
            Doc(
                """
                `max_retries`: Defines how many times a task should be retried after failure.
                Once this limit is reached, the task will be marked as failed and no further retries will be attempted.

                The default value of `max_retries` is 3.

                You can override the `max_retries` setting either globally (in Celery's configuration) or
                on a per-task basis (in the task definition).

                Examples:
                    @app.task(bind=True, max_retries=3)
                    def add(data):
                        try:
                            if data == "error":
                                raise Exception("Something went wrong!")
                            return f"Processed {data}"
                        except Exception as e:
                            self.retry(exc=e, countdown=10)
                """
            ),
        ] = 3,
        default_retry_delay: Annotated[
            int,
            Doc(
                """
                default_retry_delay: It specifies the default time (in seconds) to wait before
                retrying a task that failed, if no specific retry delay (countdown) is provided.

                The default value of default_retry_delay is 300 seconds (5 minutes).

                This value can be overridden on a per-task basis or globally in the Celery configuration.

                Examples:
                    @app.task(bind=True, max_retries=3, default_retry_delay=300)
                    def add(data):
                        try:
                            if data == "error":
                                raise Exception("Something went wrong!")
                            return f"Processed {data}"
                        except Exception as e:
                            self.retry(exc=e)
                """
            ),
        ] = 3 * MINUTES,
        rate_limit: Annotated[
            int | float | str | None,
            Doc(
                """
                Set the rate limit for this task type (limits the number of tasks that can be run
                in a given time frame).  Tasks will still complete when a rate limit is in effect,
                but it may take some time before it’s allowed to start.

                If this is None no rate limit is in effect.  If it is an integer or float,
                it is interpreted as “tasks per second”.

                The rate limits can be specified in seconds, minutes or hours by appending
                “/s”, “/m” or “/h” to the value.  Tasks will be evenly distributed over the specified time frame.

                Example: “100/m” (hundred tasks a minute).
                This will enforce a minimum delay of 600ms between starting two tasks on the same worker instance.

                Default is the task_default_rate_limit setting:
                if not specified means rate limiting for tasks is disabled by default.

                Note that this is a per worker instance rate limit, and not a global rate limit.
                To enforce a global rate limit (e.g., for an API with a maximum number of requests per second),
                you must restrict to a given queue.

                Examples:
                    @app.task(rate_limit="100/m")
                    def add():
                        return "Fetched data"
                """
            ),
        ] = None,
        time_limit: Annotated[
            int | None,
            Doc(
                """
                time_limit: Defines the maximum execution time for a task.
                If the task takes longer than the specified time limit, it will be terminated.

                The value of time_limit is provided in seconds.

                Default behavior: When not set the workers default is used.

                You can set time_limit both globally (in Celery's configuration) or on a per-task basis.

                Examples:
                    @app.task(time_limit=10)
                    def process_data(data):
                        print(f"Processing {data}")
                        import time
                        time.sleep(20)
                        return f"Processed {data}"
                """
            ),
        ] = None,
        soft_time_limit: Annotated[
            int | None,
            Doc(
                """
                soft_time_limit: Defines the time (in seconds) that a task is allowed to run before
                Celery sends a soft timeout signal (a SoftTimeLimitExceeded exception).

                Graceful Handling: When the soft time limit is exceeded,
                Celery raises a SoftTimeLimitExceeded exception inside the task,
                giving the task a chance to handle the situation (e.g., by performing cleanup or logging).

                time_limit: Works in tandem with soft_time_limit.
                If the task does not stop after the soft_time_limit,
                the hard time limit (time_limit) will forcibly terminate the task.

                Examples:
                    @app.task(time_limit=15, soft_time_limit=10)
                    def process_data(data):
                        try:
                            print(f"Processing {data}...")
                            for i in range(1, 21):
                                print(f"Processing step {i} of 20")
                                time.sleep(1)
                        except SoftTimeLimitExceeded:
                            print(f"Soft time limit exceeded, stopping task gracefully...")
                        return f"Processed {data}"
                """
            ),
        ] = None,
        priority: Annotated[
            int,
            Doc(
                """
                priority: This is an integer value that determines the priority of a task.
                The lower the value, the higher the priority.

                A lower number means higher priority.

                A higher number means lower priority.

                Default Value: If you do not specify a priority,
                the task will be assigned the default priority, which is typically 0 (neutral priority).

                Priority and Queues: Celery uses brokers (like RabbitMQ or Redis),
                and they support task prioritization. However, the ability to prioritize tasks depends
                on the message broker being used. For example, RabbitMQ supports priorities natively,
                but Redis does not directly support prioritizing tasks. For Redis,
                priority will be simulated through task ordering.

                Examples:
                    @app.task(priority=0)
                    def process_data(data):
                        print(f"Processing data: {data}")
                        return f"Processed {data}"
                """
            ),
        ] = 0,
        ignore_result: Annotated[
            bool,
            Doc(
                """
                ignore_result=True: When this option is set to True,
                Celery will not store the result of the task. The result will not be sent to the backend,
                so calling task.result or trying to retrieve the result later will not work.

                ignore_result=False (default): Celery will store the task result in the result backend.
                You can retrieve the result of the task using task.result or AsyncResult.get().

                Examples:
                    @app.task(ignore_result=True)
                    def send_email(recipient, subject, body):
                        # Simulate sending an email
                        print(f"Sending email to {recipient} with subject '{subject}'")
                        # No result is needed, so we ignore it
                        return "Email sent"
                """
            ),
        ] = False,
        store_errors_even_if_ignored: Annotated[
            bool,
            Doc(
                """
                store_errors_even_if_ignored=True: When this option is set to True,
                Celery will store any exceptions (errors) raised during the execution of the task,
                even if the task is configured to ignore its result.
                This can be useful for logging errors or tracking task failures,
                even when you don't care about the results themselves.

                Examples:
                    @app.task(ignore_result=True, store_errors_even_if_ignored=True)
                    def process_data(data):
                        if data == "bad":
                            raise ValueError("An error occurred while processing data.")
                        print(f"Processing data: {data}")
                        return "Success"
                """
            ),
        ] = False,
        autoretry_for: Annotated[
            tuple[type[Exception]],
            Doc(
                """
                autoretry_for: This option is used to define a list of exceptions that,
                when raised during the execution of the task, will trigger an automatic retry.
                The task will attempt to execute again without you needing to manually invoke the retry logic.
                """
            ),
        ] = (),  # type: ignore
        retry_backoff: Annotated[
            bool,
            Doc(
                """
                retry_backoff=True: This enables exponential backoff,
                meaning that after each failure, the retry delay will increase exponentially.
                """
            ),
        ] = False,
        retry_backoff_max: Annotated[
            int,
            Doc(
                """
                retry_backoff_max: This is an optional setting that defines the maximum retry delay.
                Even with exponential backoff, the retry delay will not exceed this value.
                """
            ),
        ] = 600,
        queue: Annotated[
            str | None,
            Doc(
                """
                Queue: A logical container where tasks are placed to be picked up by workers.
                In Celery, queues are implemented using the message broker (such as RabbitMQ or Redis).

                Task Routing: The queue option helps route specific tasks to different queues,
                so workers can process them independently, allowing you to manage load balancing,
                prioritization, and task segregation.

                Multiple Queues: In a Celery setup, you can have multiple queues,
                and workers can subscribe to one or more of them. This allows for better organization,
                especially when you have different types of tasks that require different resources or processing times.

                Examples:
                    @app.task(queue='high_priority')
                    def high_priority_task():
                        print("Processing high-priority task")

                    @app.task(queue='low_priority')
                    def low_priority_task():
                        print("Processing low-priority task")
                """
            ),
        ] = None,
        track_started: Annotated[
            bool,
            Doc(
                """
                If True the task will report its status as “started” when the task is executed by a worker.
                The default value is False as the normal behavior is to not report that level of granularity.
                Tasks are either pending, finished, or waiting to be retried.
                Having a “started” status can be useful for when there are long running tasks and
                there’s a need to report what task is currently running.
                """
            ),
        ] = False,
        **kwargs: Annotated[
            dict[str, Any],
            Doc(
                """
                Celery kwargs.
                """
            ),
        ],
    ) -> type[Task]:
        # Added common parameters and corresponding annotations for Celery tasks, and by
        # default inherited from the Task class to support async def asynchronous function execution.
        return super().task(
            *args,
            name=name,
            base=base,
            bind=bind,
            acks_late=acks_late,
            max_retries=max_retries,
            default_retry_delay=default_retry_delay,
            rate_limit=rate_limit,
            priority=priority,
            ignore_result=ignore_result,
            time_limit=time_limit,
            soft_time_limit=soft_time_limit,
            autoretry_for=autoretry_for,
            retry_backoff=retry_backoff,
            retry_backoff_max=retry_backoff_max,
            queue=queue,
            store_errors_even_if_ignored=store_errors_even_if_ignored,
            track_started=track_started,
            **kwargs,
        )
