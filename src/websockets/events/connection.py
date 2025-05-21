"""
Author  : Coke
Date    : 2025-05-16
"""

from typing import Literal

from src.core.config import auth_settings
from src.deps.auth import AuthCrudDep
from src.deps.database import RedisDep
from src.schemas import BaseModel
from src.utils.security import decode_token
from src.websockets.app import socket
from src.websockets.params import SID

user_sid_structure = "user:<{user_id}>:sid"
sid_user_structure = "sid:<{sid}>:user"
online_users_structure = "online_users"


class RedisUser(BaseModel):
    id: str
    name: str


class User(BaseModel):
    name: str


class AccessToken(BaseModel):
    access_token: str


@socket.event
async def connect(sid: SID, auth: AccessToken, db_user: AuthCrudDep, redis: RedisDep) -> Literal[False] | None:
    token = auth.access_token
    if not token:
        return False

    user = decode_token(token, auth_settings.ACCESS_TOKEN_KEY)

    user_info = await db_user.get(user.user_id)
    if not user_info:
        return False

    user_id = str(user_info.id)
    await redis.set(sid_user_structure.format(sid=sid), RedisUser(id=user_id, name=user_info.name).model_dump())
    await redis.set(user_sid_structure.format(user_id=user_id), sid)
    await redis.set(online_users_structure, {user_id})

    return None


# @socket.on("test")
# async def test(sid: SID, data1: User, redis: RedisDep) -> None:
#     data = await redis.get("test_123")
#     print(data, data1, sid)


@socket.event
async def disconnect(sid: SID, redis: RedisDep) -> None:
    user = await redis.get_mapping(sid_user_structure.format(sid=sid))
    user_info = RedisUser.model_validate(user)
    await redis.delete(sid_user_structure.format(sid=sid))
    await redis.delete(user_sid_structure.format(user_id=user_info.id))
    await redis.delete_set(online_users_structure, user_info.id)
