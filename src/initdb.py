"""
Init database.

Author  : Coke
Date    : 2025-04-18
"""

import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import AsyncSessionLocal
from src.models.auth import User
from src.schemas.auth import UserCreate
from src.utils.security import hash_password

users: list[UserCreate] = [
    UserCreate(name="admin", email="admin@gmail.com", username="admin", password="123456"),  # type: ignore
]


async def create_user(session: AsyncSession) -> None:
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
