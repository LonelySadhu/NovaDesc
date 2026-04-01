from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from domain.equipment.value_objects import MaintenanceIntervalUnit


class MaintenanceScheduleCreate(BaseModel):
    equipment_id: UUID
    title: str
    description: str
    interval_value: int
    interval_unit: MaintenanceIntervalUnit


class MaintenanceScheduleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    interval_value: Optional[int] = None
    interval_unit: Optional[MaintenanceIntervalUnit] = None
    is_active: Optional[bool] = None


class RecordCompletion(BaseModel):
    performed_at: datetime


class MaintenanceScheduleResponse(BaseModel):
    id: UUID
    equipment_id: UUID
    title: str
    description: str
    interval_value: int
    interval_unit: MaintenanceIntervalUnit
    last_performed_at: Optional[datetime]
    next_due_at: Optional[datetime]
    is_active: bool
    is_overdue: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
