from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from .value_objects import SerialNumber, MaintenanceInterval, EquipmentStatus


@dataclass
class Equipment:
    name: str
    serial_number: SerialNumber
    manufacturer: str
    model: str
    location: str
    status: EquipmentStatus = EquipmentStatus.ACTIVE
    maintenance_interval: Optional[MaintenanceInterval] = None
    installed_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def decommission(self) -> None:
        self.status = EquipmentStatus.DECOMMISSIONED
        self.updated_at = datetime.utcnow()

    def set_under_maintenance(self) -> None:
        self.status = EquipmentStatus.UNDER_MAINTENANCE
        self.updated_at = datetime.utcnow()

    def restore(self) -> None:
        self.status = EquipmentStatus.ACTIVE
        self.updated_at = datetime.utcnow()


@dataclass
class EquipmentComponent:
    equipment_id: UUID
    name: str
    part_number: str
    quantity: int = 1
    notes: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
