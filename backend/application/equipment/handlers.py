from datetime import datetime
from uuid import UUID

from domain.equipment.entities import Equipment
from domain.equipment.repositories import EquipmentRepository
from domain.equipment.value_objects import SerialNumber, MaintenanceInterval

from .commands import CreateEquipmentCommand, UpdateEquipmentCommand, DecommissionEquipmentCommand


class EquipmentCommandHandler:
    def __init__(self, repository: EquipmentRepository):
        self._repo = repository

    async def create(self, cmd: CreateEquipmentCommand) -> Equipment:
        existing = await self._repo.get_by_serial(cmd.serial_number)
        if existing:
            raise ValueError(f"Equipment with serial '{cmd.serial_number}' already exists")

        interval = None
        if cmd.interval_value and cmd.interval_unit:
            interval = MaintenanceInterval(value=cmd.interval_value, unit=cmd.interval_unit)

        equipment = Equipment(
            name=cmd.name,
            serial_number=SerialNumber(cmd.serial_number),
            manufacturer=cmd.manufacturer,
            model=cmd.model,
            location=cmd.location,
            maintenance_interval=interval,
            installed_at=datetime.fromisoformat(cmd.installed_at) if cmd.installed_at else None,
            metadata=cmd.metadata or {},
        )
        return await self._repo.save(equipment)

    async def update(self, cmd: UpdateEquipmentCommand) -> Equipment:
        equipment = await self._repo.get_by_id(cmd.equipment_id)
        if not equipment:
            raise ValueError(f"Equipment {cmd.equipment_id} not found")

        if cmd.name:
            equipment.name = cmd.name
        if cmd.location:
            equipment.location = cmd.location
        if cmd.interval_value and cmd.interval_unit:
            equipment.maintenance_interval = MaintenanceInterval(
                value=cmd.interval_value, unit=cmd.interval_unit
            )
        if cmd.metadata is not None:
            equipment.metadata = cmd.metadata

        equipment.updated_at = datetime.utcnow()
        return await self._repo.save(equipment)

    async def decommission(self, cmd: DecommissionEquipmentCommand) -> Equipment:
        equipment = await self._repo.get_by_id(cmd.equipment_id)
        if not equipment:
            raise ValueError(f"Equipment {cmd.equipment_id} not found")
        equipment.decommission()
        return await self._repo.save(equipment)
