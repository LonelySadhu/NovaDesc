from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from domain.equipment.value_objects import EquipmentStatus, MaintenanceIntervalUnit, SystemStatus


class MaintenanceIntervalSchema(BaseModel):
    value: int
    unit: MaintenanceIntervalUnit


# ── Equipment System ──────────────────────────────────────────────────────────

class EquipmentSystemCreate(BaseModel):
    name: str
    department_id: UUID
    description: Optional[str] = None
    system_type: Optional[str] = None
    stakeholder_id: Optional[UUID] = None


class EquipmentSystemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_type: Optional[str] = None
    stakeholder_id: Optional[UUID] = None


class EquipmentSystemResponse(BaseModel):
    id: UUID
    name: str
    department_id: UUID
    description: Optional[str]
    system_type: Optional[str]
    stakeholder_id: Optional[UUID]
    status: SystemStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Equipment ─────────────────────────────────────────────────────────────────

class EquipmentCreate(BaseModel):
    name: str
    serial_number: str
    manufacturer: str
    model: str
    location: str
    system_id: UUID
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
    system_id: UUID
    status: EquipmentStatus
    maintenance_interval: Optional[MaintenanceIntervalSchema] = None
    installed_at: Optional[datetime] = None
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
