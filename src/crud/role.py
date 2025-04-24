"""
User Roles CRUD.

Author  : Coke
Date    : 2025-04-24
"""

from sqlmodel.ext.asyncio.session import AsyncSession

from src.crud.base import BaseSQLModelCRUD
from src.models.auth import Role
from src.schemas.role import RoleCreate, RoleUpdate


class RoleCRUD(BaseSQLModelCRUD[Role, RoleCreate, RoleUpdate]):
    """Role CRUD operations using SQLAlchemy."""

    async def get_role_by_codes(self, codes: list[str], *, session: AsyncSession | None = None) -> list[Role]:
        """
        Retrieve a list of roles based on the provided role codes.

        Args:
            codes (List[str]): A list of role codes to filter roles by.
            session (Optional[AsyncSession], optional): An optional SQLAlchemy `AsyncSession` object.
                If not provided, the default session will be used.

        Returns:
            List[Role]: A list of `Role` objects that match the given role codes.
        """
        session = session or self.session
        roles = await self.get_all(self.model.code.in_(codes), session=session)  # type: ignore
        return roles
