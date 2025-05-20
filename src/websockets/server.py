"""
Author  : Coke
Date    : 2025-05-16
"""

import asyncio
from typing import Any, Awaitable, Callable, TypeVar, overload

from fastapi import status
from pydantic import BaseModel, ValidationError
from socketio import AsyncServer as SocketIOAsyncServer

from src.schemas.response import SocketErrorResponse
from src.utils.utils import format_validation_errors
from src.websockets.dependencies.core import LifespanContext, solve_dependency

T = TypeVar("T")


class AsyncServer(SocketIOAsyncServer):
    """"""

    def __init__(self, cors_allowed_origins: str | list[str] | None = None, **kwargs: Any) -> None:
        if cors_allowed_origins is not None and "*" in cors_allowed_origins:
            cors_allowed_origins = "*"
        super().__init__(cors_allowed_origins=cors_allowed_origins, **kwargs)

    def on(self, event: str, handler: Callable | None = None, namespace: str | None = None) -> Callable:
        """
        Decorator for registering an event handler with dependency injection support.

        This method wraps the provided handler function and automatically resolves its
        dependencies using a custom dependency system. It supports context teardown,
        validation error handling, and emits error messages back to the client if needed.

        Args:
            event (str): The event name to bind the handler to.
            handler (Callable | None, optional): The event handler function. If None, the decorator is returned.
            namespace (str | None, optional): An optional namespace for the event.

        Returns:
            Callable: The decorator function or the original handler if one was provided.
        """

        def decorator(func: Callable) -> Callable:
            async def wrapper(sid: str, *args: Any, **kwargs: Any) -> None:
                context = LifespanContext()
                cache: dict[Any, Any] = {}

                data = args[0] if args else None
                environ = kwargs.get("environ", {})

                cache["__sid__"] = sid
                cache["__data__"] = data
                cache["__environ__"] = environ

                try:
                    await solve_dependency(func, context, cache)

                except ValidationError as e:
                    details = format_validation_errors(e)
                    await self.emit(
                        "error",
                        SocketErrorResponse(
                            code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
                            event=event,
                            message="Data Validation Error.",
                            data=details,
                        ),
                        to=sid,
                    )

                except TypeError:
                    await self.emit(
                        "error",
                        SocketErrorResponse(
                            code=status.WS_1003_UNSUPPORTED_DATA,
                            event=event,
                            message="Data Type Error.",
                            data=f"TypeError: expected a 'map', but received an '{type(data).__name__}'.",
                        ),
                        to=sid,
                    )

                finally:
                    await context.run_teardowns()

            return super(AsyncServer, self).on(event=event, handler=handler, namespace=namespace)(wrapper)

        return decorator if handler is None else decorator(handler)

    async def emit(
        self,
        event: str,
        data: Any | None = None,
        *,
        to: str | None = None,
        room: str | None = None,
        skip_sid: str | list[str] | None = None,
        namespace: str | None = None,
        callback: Callable | None = None,
        ignore_queue: bool = False,
        serializer: str = "serializable_dict",
    ) -> Awaitable[None]:
        """
        Emit an event to clients, optionally including data, specific room or namespace.

        Args:
            event (str): The event name to emit.
            data (Any | None, optional): The data to send with the event.
            to (str | None, optional): The specific client ID(s) to send the event to.
            room (str | None, optional): The room to send the event to.
            skip_sid (str | list[str] | None, optional): The session ID(s) to skip when emitting the event.
            namespace (str | None, optional): The namespace in which to emit the event.
            callback (Callable | None, optional): A callback function to invoke when the emit operation is complete.
            ignore_queue (bool, optional): Whether to ignore the event queue.
            serializer (str, optional): The method name used to serialize the model.

        Returns:
            Awaitable[None]: An awaitable object indicating when the emit operation is complete.
        """
        data = self._pydantic_model_to_dict(data, serializer=serializer)
        return await super().emit(
            event=event,
            data=data,
            to=to,
            room=room,
            skip_sid=skip_sid,
            namespace=namespace,
            callback=callback,
            ignore_queue=ignore_queue,
        )

    async def send(
        self,
        data: Any,
        *,
        to: str | None = None,
        room: str | None = None,
        skip_sid: str | list[str] | None = None,
        namespace: str | None = None,
        callback: Callable | None = None,
        ignore_queue: bool = False,
        serializer: str = "serializable_dict",
    ) -> Awaitable[None]:
        """
        Send a message with optional routing details, such as specific client(s), room, or namespace.

        Args:
            data (Any): The data to send.
            to (str | None, optional): The specific client ID(s) to send the message to.
            room (str | None, optional): The room to send the message to.
            skip_sid (str | list[str] | None, optional): The session ID(s) to skip when sending the message.
            namespace (str | None, optional): The namespace in which to send the message.
            callback (Callable | None, optional): A callback function to invoke when the send operation is complete.
            ignore_queue (bool, optional): Whether to ignore the message queue. Defaults to False.
            serializer (str, optional): The method name used to serialize the model.

        Returns:
            Awaitable[None]: An awaitable object indicating when the send operation is complete.
        """
        return await self.emit(
            "message",
            data=data,
            to=to,
            room=room,
            skip_sid=skip_sid,
            namespace=namespace,
            callback=callback,
            ignore_queue=ignore_queue,
            serializer=serializer,
        )

    async def _trigger_event(self, event: str, namespace: str, *args: Any) -> Awaitable[None] | None:
        """
        Trigger an application-level event handler.

        This method attempts to locate and invoke a registered event handler
        (either a specific event handler or a namespace-level handler).
        It supports both coroutine and regular function handlers.

        Args:
            event (str): The name of the event to trigger (e.g., "connect").
            namespace (str): The namespace associated with the event.
            *args (Any): Positional arguments to pass to the event handler.
                For "connect" events, the expected order is (sid, environ, data).

        Returns:
            Awaitable[None] | None: The return value from the event handler,
            or `self.not_handled` if no handler was found.
        """
        handler, args = self._get_event_handler(event, namespace, args)
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    ret = await self._call_handler(handler, event, args)
                else:
                    ret = self._call_handler(handler, event, args)
            except asyncio.CancelledError:
                ret = None
            return ret

        handler, args = self._get_namespace_handler(namespace, args)
        if handler:
            return await handler.trigger_event(event, *args)

        else:
            return self.not_handled

    @staticmethod
    def _call_handler(handler: Callable, event: str, args: tuple) -> Any:
        """
        Call the given event handler with appropriate arguments.

        For "connect" events, this method injects the `environ` argument
        as a keyword parameter, while preserving `sid` and `data` as positional arguments.
        For "disconnect", it removes the last argument for backward compatibility.

        Args:
            handler (Callable): The function or coroutine to call.
            event (str): The name of the event ("connect", "disconnect", etc.).
            args (tuple): The arguments to pass to the handler.

        Returns:
            Any: The return value from the handler.
        """
        if event == "connect":
            if len(args) == 3:
                return handler(args[0], args[2], environ=args[1])
            elif len(args) == 2:
                return handler(args[0], environ=args[1])
            else:
                return handler(*args)
        elif event == "disconnect":
            return handler(*args[:-1])
        else:
            return handler(*args)

    @staticmethod
    @overload
    def _pydantic_model_to_dict(data: BaseModel, serializer: str = "serializable_dict") -> dict: ...

    @staticmethod
    @overload
    def _pydantic_model_to_dict(data: T, serializer: str = "serializable_dict") -> T: ...

    @staticmethod
    def _pydantic_model_to_dict(data: BaseModel | T, serializer: str = "serializable_dict") -> dict | T:
        """
        Converts a Pydantic model to a dictionary using a specified serializer method.

        If the input `data` is an instance of BaseModel, it will try to use the
        specified serializer method (e.g., `serializable_dict`). If the method does not exist,
        it will fall back to using `model_dump()` (Pydantic v2).

        Args:
            data (BaseModel | T): The data to convert. If it's a Pydantic model, it will be converted.
            serializer (str, optional): The method name used to serialize the model.

        Returns:
            dict | T: A dictionary if `data` is a Pydantic model, otherwise returns `data` unchanged.
        """
        if isinstance(data, BaseModel):
            if serializer != "model_dump" and hasattr(data, serializer):
                return getattr(data, serializer)()

            return data.model_dump()

        return data
