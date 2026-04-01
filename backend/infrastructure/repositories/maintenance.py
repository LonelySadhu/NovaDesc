from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.equipment.value_objects import MaintenanceIntervalUnit
from domain.maintenance.entities import MaintenanceSchedule
from domain.maintenance.repositories import MaintenanceScheduleRepository
from infrastructure.database.models.maintenance import MaintenanceScheduleModel


class SqlMaintenanceScheduleRepository(MaintenanceScheduleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, schedule_id: UUID) -> Optional[MaintenanceSchedule]:
        row = await self._session.get(MaintenanceScheduleModel, schedule_id)
        return self._to_entity(row) if row else None

    async def list_by_equipment(
        self, equipment_id: UUID, active_only: bool = False
    ) -> List[MaintenanceSchedule]:
        stmt = select(MaintenanceScheduleModel).where(
            MaintenanceScheduleModel.equipment_id == equipment_id
        )
        if active_only:
            stmt = stmt.where(MaintenanceScheduleModel.is_active.is_(True))
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars()]

    async def list_overdue(self) -> List[MaintenanceSchedule]:
        now = datetime.utcnow()
        result = await self._session.execute(
            select(MaintenanceScheduleModel).where(
                MaintenanceScheduleModel.next_due_at < now,
                MaintenanceScheduleModel.is_active.is_(True),
            )
        )
        return [self._to_entity(row) for row in result.scalars()]

    async def save(self, schedule: MaintenanceSchedule) -> None:
        row = await self._session.get(MaintenanceScheduleModel, schedule.id)
        if row is None:
            row = MaintenanceScheduleModel(
                id=schedule.id,
                equipment_id=schedule.equipment_id,
                title=schedule.title,
                description=schedule.description,
                interval_value=schedule.interval_value,
                interval_unit=schedule.interval_unit.value,
                last_performed_at=schedule.last_performed_at,
                next_due_at=schedule.next_due_at,
                is_active=schedule.is_active,
                created_at=schedule.created_at,
            )
            self._session.add(row)
        else:
            row.equipment_id = schedule.equipment_id
            row.title = schedule.title
            row.description = schedule.description
            row.interval_value = schedule.interval_value
            row.interval_unit = schedule.interval_unit.value
            row.last_performed_at = schedule.last_performed_at
            row.next_due_at = schedule.next_due_at
            row.is_active = schedule.is_active
        await self._session.flush()

    async def delete(self, schedule_id: UUID) -> None:
        row = await self._session.get(MaintenanceScheduleModel, schedule_id)
        if row:
            await self._session.delete(row)
            await self._session.flush()

    @staticmethod
    def _to_entity(row: MaintenanceScheduleModel) -> MaintenanceSchedule:
        return MaintenanceSchedule(
            id=row.id,
            equipment_id=row.equipment_id,
            title=row.title,
            description=row.description,
            interval_value=row.interval_value,
            interval_unit=MaintenanceIntervalUnit(row.interval_unit),
            last_performed_at=row.last_performed_at,
            next_due_at=row.next_due_at,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )