"""
Author  : Coke
Date    : 2025-05-19
"""

from importlib import util
from pathlib import Path

from socketio import ASGIApp, AsyncRedisManager

from src.core.config import settings
from src.websockets.server import AsyncServer


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
