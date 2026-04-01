from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.equipment.entities import Equipment, EquipmentSystem
from domain.equipment.repositories import EquipmentRepository, EquipmentSystemRepository
from domain.equipment.value_objects import (
    EquipmentStatus,
    MaintenanceInterval,
    MaintenanceIntervalUnit,
    SerialNumber,
    SystemStatus,
)
from infrastructure.database.models.equipment import EquipmentModel, EquipmentSystemModel


class SqlEquipmentSystemRepository(EquipmentSystemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, system_id: UUID) -> Optional[EquipmentSystem]:
        row = await self._session.get(EquipmentSystemModel, system_id)
        return self._to_entity(row) if row else None

    async def list_by_department(self, department_id: UUID) -> List[EquipmentSystem]:
        result = await self._session.execute(
            select(EquipmentSystemModel).where(
                EquipmentSystemModel.department_id == department_id
            )
        )
        return [self._to_entity(row) for row in result.scalars()]

    async def save(self, system: EquipmentSystem) -> None:
        row = await self._session.get(EquipmentSystemModel, system.id)
        if row is None:
            row = EquipmentSystemModel(
                id=system.id,
                name=system.name,
                description=system.description,
                system_type=system.system_type,
                department_id=system.department_id,
                stakeholder_id=system.stakeholder_id,
                status=system.status.value,
                created_at=system.created_at,
            )
            self._session.add(row)
        else:
            row.name = system.name
            row.description = system.description
            row.system_type = system.system_type
            row.department_id = system.department_id
            row.stakeholder_id = system.stakeholder_id
            row.status = system.status.value
        await self._session.flush()

    async def delete(self, system_id: UUID) -> None:
        row = await self._session.get(EquipmentSystemModel, system_id)
        if row:
            await self._session.delete(row)
            await self._session.flush()

    @staticmethod
    def _to_entity(row: EquipmentSystemModel) -> EquipmentSystem:
        return EquipmentSystem(
            id=row.id,
            name=row.name,
            description=row.description,
            system_type=row.system_type,
            department_id=row.department_id,
            stakeholder_id=row.stakeholder_id,
            status=SystemStatus(row.status),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class SqlEquipmentRepository(EquipmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, equipment_id: UUID) -> Optional[Equipment]:
        row = await self._session.get(EquipmentModel, equipment_id)
        return self._to_entity(row) if row else None

    async def get_by_serial(self, serial: str) -> Optional[Equipment]:
        result = await self._session.execute(
            select(EquipmentModel).where(EquipmentModel.serial_number == serial)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def list(
        self,
        system_id: Optional[UUID] = None,
        status: Optional[EquipmentStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Equipment]:
        stmt = select(EquipmentModel)
        if system_id is not None:
            stmt = stmt.where(EquipmentModel.system_id == system_id)
        if status is not None:
            stmt = stmt.where(EquipmentModel.status == status.value)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars()]

    async def save(self, equipment: Equipment) -> None:
        row = await self._session.get(EquipmentModel, equipment.id)
        mi = equipment.maintenance_interval
        if row is None:
            row = EquipmentModel(
                id=equipment.id,
                name=equipment.name,
                serial_number=equipment.serial_number.value,
                manufacturer=equipment.manufacturer,
                model=equipment.model,
                location=equipment.location,
                system_id=equipment.system_id,
                status=equipment.status.value,
                maintenance_interval_value=mi.value if mi else None,
                maintenance_interval_unit=mi.unit.value if mi else None,
                installed_at=equipment.installed_at,
                metadata_=equipment.metadata,
                created_at=equipment.created_at,
            )
            self._session.add(row)
        else:
            row.name = equipment.name
            row.serial_number = equipment.serial_number.value
            row.manufacturer = equipment.manufacturer
            row.model = equipment.model
            row.location = equipment.location
            row.system_id = equipment.system_id
            row.status = equipment.status.value
            row.maintenance_interval_value = mi.value if mi else None
            row.maintenance_interval_unit = mi.unit.value if mi else None
            row.installed_at = equipment.installed_at
            row.metadata_ = equipment.metadata
        await self._session.flush()

    async def delete(self, equipment_id: UUID) -> None:
        row = await self._session.get(EquipmentModel, equipment_id)
        if row:
            await self._session.delete(row)
            await self._session.flush()

    @staticmethod
    def _to_entity(row: EquipmentModel) -> Equipment:
        mi = None
        if row.maintenance_interval_value is not None and row.maintenance_interval_unit is not None:
            mi = MaintenanceInterval(
                value=row.maintenance_interval_value,
                unit=MaintenanceIntervalUnit(row.maintenance_interval_unit),
            )
        return Equipment(
            id=row.id,
            name=row.name,
            serial_number=SerialNumber(row.serial_number),
            manufacturer=row.manufacturer,
            model=row.model,
            location=row.location,
            system_id=row.system_id,
            status=EquipmentStatus(row.status),
            maintenance_interval=mi,
            installed_at=row.installed_at,
            metadata=row.metadata_,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
