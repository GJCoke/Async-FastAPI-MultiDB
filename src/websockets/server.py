"""
Author  : Coke
Date    : 2025-05-16
"""

from inspect import isclass, signature
from typing import Any, Awaitable, Callable, TypeVar, get_type_hints, overload

from fastapi import status
from pydantic import BaseModel, ValidationError
from pydantic._internal._model_construction import ModelMetaclass
from socketio import AsyncServer as SocketIOAsyncServer

from src.schemas.response import WSErrorResponse
from src.utils.utils import format_validation_errors

T = TypeVar("T")


class AsyncServer(SocketIOAsyncServer):
    """"""

    def __init__(self, cors_allowed_origins: str | list[str] | None = None, **kwargs: Any) -> None:
        if cors_allowed_origins is not None and "*" in cors_allowed_origins:
            cors_allowed_origins = "*"
        super().__init__(cors_allowed_origins=cors_allowed_origins, **kwargs)

    def on(
        self,
        event: str,
        handler: Callable | None = None,
        namespace: str | None = None,
    ) -> Callable[[Callable], Callable]:
        """
        Registers an event listener with optional automatic Pydantic validation.

        Args:
            event (str): The name of the event to listen for.
            handler (Optional[Callable], optional): The event handler function.
            namespace (Optional[str], optional): The namespace for the event.

        Returns:
            Callable[[Callable], Callable]: A decorator that wraps the event handler function.
        """

        def decorator(func: Callable) -> Callable:
            """
            Decorator that wraps the original event handler.

            Args:
                func (Callable): The original handler function.

            Returns:
                Callable: The wrapped handler or the original if no validation is required.
            """
            sig = signature(func)
            params = list(sig.parameters.values())

            if len(params) < 2:
                return super(AsyncServer, self).on(event=event, handler=handler, namespace=namespace)(func)

            data_param = params[1]
            annotations = get_type_hints(func)
            model_cls = annotations.get(data_param.name)

            if model_cls is not None and isclass(model_cls) and isinstance(model_cls, ModelMetaclass):

                async def wrapper(sid: str, data: dict, *args: Any, **kwargs: Any) -> Any:
                    """
                    Wrapper function that validates incoming data using a Pydantic model.

                    Args:
                        sid (str): The session ID of the client.
                        data (dict): The raw data received from the client.
                        *args (Any): Additional positional arguments.
                        **kwargs (Any): Additional keyword arguments.

                    Returns:
                        Any: The result of the original handler, or an error response if validation fails.
                    """
                    try:
                        parsed_data = model_cls(**data)
                        return await func(sid, parsed_data, *args, **kwargs)
                    except ValidationError as e:
                        "[{'type': 'missing', 'loc': ['name'], 'msg': 'Field required', 'input': {'name1': 'coke'}}]"
                        details = format_validation_errors(e)
                        await self.emit(
                            "error",
                            WSErrorResponse(
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
                            WSErrorResponse(
                                code=status.WS_1003_UNSUPPORTED_DATA,
                                event=event,
                                message="Data Type Error.",
                                data=f"TypeError: expected a 'map', but received an '{type(data).__name__}'.",
                            ),
                            to=sid,
                        )

                return super(AsyncServer, self).on(event=event, handler=handler, namespace=namespace)(wrapper)

            return super(AsyncServer, self).on(event=event, handler=handler, namespace=namespace)(func)

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

    @overload
    @staticmethod
    def _pydantic_model_to_dict(data: BaseModel, serializer: str = "serializable_dict") -> dict: ...

    @overload
    @staticmethod
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
