"""
Init database.

Author  : Coke
Date    : 2025-04-18
"""

import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import AsyncSessionLocal
from src.models.auth import Role, User
from src.schemas.auth import UserCreate
from src.schemas.role import RoleCreate
from src.utils.security import hash_password

USERNAME = "admin"
PASSWORD = "123456"

roles: list[RoleCreate] = [
    RoleCreate(
        name="admin",
        description="Administrator",
        code="ADMIN",
        interface_permissions=["GET:/api/v1/router/backend"],
    ),
]

users: list[UserCreate] = [
    UserCreate(
        name="admin", email="admin@gmail.com", username=USERNAME, password=PASSWORD, is_admin=True, roles=["ADMIN"]
    ),  # type: ignore
]


async def create_user(session: AsyncSession) -> None:
    for role in roles:
        session.add(Role.model_validate(role))

    for user in users:
        user_dict = user.serializable_dict()
        user_dict["password"] = hash_password(user.password)
        session.add(User.model_validate(user_dict))

    await session.commit()


async def init_db() -> None:
    async with AsyncSessionLocal() as session:
        await create_user(session)


if __name__ == "__main__":
    asyncio.run(init_db())
