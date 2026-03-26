from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from domain.equipment.value_objects import MaintenanceIntervalUnit


@dataclass
class CreateEquipmentCommand:
    name: str
    serial_number: str
    manufacturer: str
    model: str
    location: str
    installed_at: Optional[str] = None
    interval_value: Optional[int] = None
    interval_unit: Optional[MaintenanceIntervalUnit] = None
    metadata: dict = None


@dataclass
class UpdateEquipmentCommand:
    equipment_id: UUID
    name: Optional[str] = None
    location: Optional[str] = None
    interval_value: Optional[int] = None
    interval_unit: Optional[MaintenanceIntervalUnit] = None
    metadata: Optional[dict] = None


@dataclass
class DecommissionEquipmentCommand:
    equipment_id: UUID
