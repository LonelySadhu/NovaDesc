from datetime import datetime

from domain.equipment.entities import Equipment, EquipmentSystem
from domain.equipment.repositories import EquipmentRepository, EquipmentSystemRepository
from domain.equipment.value_objects import MaintenanceInterval, SerialNumber

from .commands import (
    CreateEquipmentCommand,
    CreateEquipmentSystemCommand,
    DecommissionEquipmentCommand,
    UpdateEquipmentCommand,
    UpdateEquipmentSystemCommand,
)


class EquipmentSystemCommandHandler:
    def __init__(self, repository: EquipmentSystemRepository) -> None:
        self._repo = repository

    async def create(self, cmd: CreateEquipmentSystemCommand) -> EquipmentSystem:
        system = EquipmentSystem(
            name=cmd.name,
            department_id=cmd.department_id,
            description=cmd.description,
            system_type=cmd.system_type,
            stakeholder_id=cmd.stakeholder_id,
        )
        await self._repo.save(system)
        return system

    async def update(self, cmd: UpdateEquipmentSystemCommand) -> EquipmentSystem:
        system = await self._repo.get_by_id(cmd.system_id)
        if not system:
            raise ValueError(f"EquipmentSystem {cmd.system_id} not found")
        if cmd.name is not None:
            system.name = cmd.name
        if cmd.description is not None:
            system.description = cmd.description
        if cmd.system_type is not None:
            system.system_type = cmd.system_type
        if cmd.stakeholder_id is not None:
            system.set_stakeholder(cmd.stakeholder_id)
        await self._repo.save(system)
        return system

    async def decommission(self, system_id) -> EquipmentSystem:
        system = await self._repo.get_by_id(system_id)
        if not system:
            raise ValueError(f"EquipmentSystem {system_id} not found")
        system.decommission()
        await self._repo.save(system)
        return system


class EquipmentCommandHandler:
    def __init__(self, repository: EquipmentRepository) -> None:
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
            system_id=cmd.system_id,
            maintenance_interval=interval,
            installed_at=cmd.installed_at,
            metadata=cmd.metadata or {},
        )
        await self._repo.save(equipment)
        return equipment

    async def update(self, cmd: UpdateEquipmentCommand) -> Equipment:
        equipment = await self._repo.get_by_id(cmd.equipment_id)
        if not equipment:
            raise ValueError(f"Equipment {cmd.equipment_id} not found")

        if cmd.name is not None:
            equipment.name = cmd.name
        if cmd.location is not None:
            equipment.location = cmd.location
        if cmd.interval_value and cmd.interval_unit:
            equipment.maintenance_interval = MaintenanceInterval(
                value=cmd.interval_value, unit=cmd.interval_unit
            )
        if cmd.metadata is not None:
            equipment.metadata = cmd.metadata

        await self._repo.save(equipment)
        return equipment

    async def decommission(self, cmd: DecommissionEquipmentCommand) -> Equipment:
        equipment = await self._repo.get_by_id(cmd.equipment_id)
        if not equipment:
            raise ValueError(f"Equipment {cmd.equipment_id} not found")
        equipment.decommission()
        await self._repo.save(equipment)
        return equipment

    async def set_fault(self, equipment_id) -> Equipment:
        equipment = await self._repo.get_by_id(equipment_id)
        if not equipment:
            raise ValueError(f"Equipment {equipment_id} not found")
        equipment.set_fault()
        await self._repo.save(equipment)
        return equipment

    async def restore(self, equipment_id) -> Equipment:
        equipment = await self._repo.get_by_id(equipment_id)
        if not equipment:
            raise ValueError(f"Equipment {equipment_id} not found")
        equipment.restore()
        await self._repo.save(equipment)
        return equipment