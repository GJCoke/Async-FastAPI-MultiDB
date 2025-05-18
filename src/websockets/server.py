"""
Author  : Coke
Date    : 2025-05-16
"""

from importlib import util
from inspect import isclass, signature
from pathlib import Path
from typing import Any, Callable, get_type_hints

from pydantic import ValidationError
from pydantic._internal._model_construction import ModelMetaclass
from socketio import ASGIApp, AsyncRedisManager
from socketio import AsyncServer as SocketIOAsyncServer

from src.core.config import settings


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
            handler (Optional[Callable], optional): The event handler function. Defaults to None.
            namespace (Optional[str], optional): The namespace for the event. Defaults to None.

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
                        await self.emit("error", {"status": 422, "event": event, "errors": e.errors()}, to=sid)

                    except TypeError:
                        await self.emit(
                            "error",
                            {
                                "status": 422,
                                "event": event,
                                "errors": f"TypeError: expected a 'map', but received an '{type(data).__name__}'.",
                            },
                            to=sid,
                        )

                return super(AsyncServer, self).on(event=event, handler=handler, namespace=namespace)(wrapper)

            return super(AsyncServer, self).on(event=event, handler=handler, namespace=namespace)(func)

        return decorator if handler is None else decorator(handler)


def auto_register_events() -> None:
    """
    Dynamically import all Python files in the 'events' directory to register Socket.IO events.

    This function scans the 'websockets/events' directory, imports all `.py` files except those starting
    with an `_` (e.g., `__init__.py`), and loads them as modules. This ensures that all
    event handlers decorated with `@socket.event` are automatically registered with the server.
    """
    base_path = Path(__file__).parent / "events"
    for file in base_path.glob("*.py"):
        if file.name.startswith("_"):
            continue

        module_name = f"websockets.events.{file.stem}"
        spec = util.spec_from_file_location(module_name, file)
        if spec is None:
            raise ImportError(f"Could not create a spec for module '{module_name}' at '{base_path}'")

        if spec.loader is None:
            raise ImportError(f"Spec loader is None for module '{module_name}' at '{base_path}'")

        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)


redis_manager = AsyncRedisManager(url=str(settings.REDIS_URL))
socket = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGINS,
    client_manager=redis_manager,
)
socket_app = ASGIApp(socket)
auto_register_events()
