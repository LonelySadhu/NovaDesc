from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users.entities import User
from domain.users.repositories import UserRepository
from domain.users.value_objects import UserRole
from infrastructure.database.models.users import UserModel


class SqlUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def list(self, limit: int = 100, offset: int = 0) -> List[User]:
        result = await self._session.execute(
            select(UserModel).limit(limit).offset(offset)
        )
        return [self._to_entity(row) for row in result.scalars()]

    async def save(self, user: User) -> User:
        row = await self._session.get(UserModel, user.id)
        if row is None:
            row = UserModel(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                department_id=user.department_id,
                created_at=user.created_at,
            )
            self._session.add(row)
        else:
            row.username = user.username
            row.email = user.email
            row.full_name = user.full_name
            row.role = user.role.value
            row.hashed_password = user.hashed_password
            row.is_active = user.is_active
            row.department_id = user.department_id
        await self._session.flush()
        return user

    @staticmethod
    def _to_entity(row: UserModel) -> User:
        return User(
            id=row.id,
            username=row.username,
            email=row.email,
            full_name=row.full_name,
            role=UserRole(row.role),
            hashed_password=row.hashed_password,
            is_active=row.is_active,
            department_id=row.department_id,
            created_at=row.created_at,
        )