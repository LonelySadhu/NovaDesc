from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from domain.equipment.value_objects import EquipmentStatus, MaintenanceIntervalUnit


class MaintenanceIntervalSchema(BaseModel):
    value: int
    unit: MaintenanceIntervalUnit


class EquipmentCreate(BaseModel):
    name: str
    serial_number: str
    manufacturer: str
    model: str
    location: str
    installed_at: Optional[datetime] = None
    maintenance_interval: Optional[MaintenanceIntervalSchema] = None
    metadata: dict = {}


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    maintenance_interval: Optional[MaintenanceIntervalSchema] = None
    metadata: Optional[dict] = None


class EquipmentResponse(BaseModel):
    id: UUID
    name: str
    serial_number: str
    manufacturer: str
    model: str
    location: str
    status: EquipmentStatus
    maintenance_interval: Optional[MaintenanceIntervalSchema] = None
    installed_at: Optional[datetime] = None
    metadata: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
