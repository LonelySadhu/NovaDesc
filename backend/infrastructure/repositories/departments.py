from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.departments.entities import Department
from domain.departments.repositories import DepartmentRepository
from infrastructure.database.models.department import DepartmentModel


class SqlDepartmentRepository(DepartmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, department_id: UUID) -> Optional[Department]:
        row = await self._session.get(DepartmentModel, department_id)
        return self._to_entity(row) if row else None

    async def list_all(self, include_inactive: bool = False) -> List[Department]:
        stmt = select(DepartmentModel)
        if not include_inactive:
            stmt = stmt.where(DepartmentModel.is_active.is_(True))
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars()]

    async def save(self, department: Department) -> None:
        row = await self._session.get(DepartmentModel, department.id)
        if row is None:
            row = DepartmentModel(
                id=department.id,
                name=department.name,
                description=department.description,
                head_id=department.head_id,
                parent_id=department.parent_id,
                is_active=department.is_active,
                created_at=department.created_at,
            )
            self._session.add(row)
        else:
            row.name = department.name
            row.description = department.description
            row.head_id = department.head_id
            row.parent_id = department.parent_id
            row.is_active = department.is_active
        await self._session.flush()

    async def delete(self, department_id: UUID) -> None:
        row = await self._session.get(DepartmentModel, department_id)
        if row:
            await self._session.delete(row)
            await self._session.flush()

    @staticmethod
    def _to_entity(row: DepartmentModel) -> Department:
        return Department(
            id=row.id,
            name=row.name,
            description=row.description,
            head_id=row.head_id,
            parent_id=row.parent_id,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
