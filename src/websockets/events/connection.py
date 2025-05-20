"""
Author  : Coke
Date    : 2025-05-16
"""

from src.deps.database import RedisDep
from src.schemas import BaseModel
from src.websockets.app import socket
from src.websockets.params import SID, Environ


class User(BaseModel):
    name: str


@socket.event
async def connect(sid: SID, environ: Environ, data: dict) -> None:
    print(sid, data, environ, "connect")


@socket.on("test")
async def test(sid: SID, data1: User, redis: RedisDep) -> None:
    data = await redis.get("test_123")
    print(data, data1, sid)


@socket.event
async def disconnect(sid: str) -> None:
    # print(sid, "disconnected")
    pass
