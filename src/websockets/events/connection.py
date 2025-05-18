"""
Author  : Coke
Date    : 2025-05-16
"""

from src.schemas import BaseModel
from src.websockets.server import socket


class User(BaseModel):
    name: str


@socket.event
async def connect(sid: str, environ: dict) -> None:
    # print(sid, environ, "connected")
    pass


@socket.on("test")
async def test(sid: str, user_info: User) -> None:
    print(sid, user_info)


@socket.event
async def disconnect(sid: str) -> None:
    pass
    # print(sid, "disconnected")
