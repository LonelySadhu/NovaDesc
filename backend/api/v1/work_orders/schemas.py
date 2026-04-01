from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from domain.work_orders.value_objects import WorkOrderPriority, WorkOrderStatus, WorkOrderType


class WorkOrderCreate(BaseModel):
    title: str
    description: str
    equipment_id: UUID
    order_type: WorkOrderType
    priority: WorkOrderPriority = WorkOrderPriority.MEDIUM
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None


class WorkOrderAssign(BaseModel):
    technician_id: UUID


class WorkOrderHold(BaseModel):
    reason: str


class WorkOrderCancel(BaseModel):
    reason: str


class WorkOrderLogCreate(BaseModel):
    message: str
    hours_spent: float = 0.0


class WorkOrderPhotoCreate(BaseModel):
    file_path: str
    original_filename: str
    file_size: int
    caption: Optional[str] = None


class WorkOrderLogResponse(BaseModel):
    id: UUID
    work_order_id: UUID
    author_id: UUID
    message: str
    hours_spent: float
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkOrderPhotoResponse(BaseModel):
    id: UUID
    work_order_id: UUID
    uploaded_by: UUID
    file_path: str
    original_filename: str
    file_size: int
    caption: Optional[str]
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class WorkOrderResponse(BaseModel):
    id: UUID
    title: str
    description: str
    equipment_id: UUID
    created_by: UUID
    order_type: WorkOrderType
    priority: WorkOrderPriority
    status: WorkOrderStatus
    assigned_to: Optional[UUID]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    on_hold_reason: Optional[str]
    cancellation_reason: Optional[str]
    total_hours: float
    logs: List[WorkOrderLogResponse] = []
    photos: List[WorkOrderPhotoResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
