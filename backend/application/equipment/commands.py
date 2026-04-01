from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from domain.equipment.value_objects import MaintenanceIntervalUnit


@dataclass
class CreateEquipmentSystemCommand:
    name: str
    department_id: UUID
    description: Optional[str] = None
    system_type: Optional[str] = None
    stakeholder_id: Optional[UUID] = None


@dataclass
class UpdateEquipmentSystemCommand:
    system_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    system_type: Optional[str] = None
    stakeholder_id: Optional[UUID] = None


@dataclass
class CreateEquipmentCommand:
    name: str
    serial_number: str
    manufacturer: str
    model: str
    location: str
    system_id: UUID
    installed_at: Optional[datetime] = None
    interval_value: Optional[int] = None
    interval_unit: Optional[MaintenanceIntervalUnit] = None
    metadata: dict = field(default_factory=dict)


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