from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from domain.spare_parts.value_objects import (
    PurchaseRequestStatus,
    SparePartStatus,
    WriteOffReason,
)


# ── Spare Part ────────────────────────────────────────────────────────────────

class SparePartCreate(BaseModel):
    equipment_id: UUID
    name: str
    part_number: str
    min_stock_level: int = 0
    unit: str = "шт."
    stock_location: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    notes: Optional[str] = None


class SparePartUpdate(BaseModel):
    name: Optional[str] = None
    min_stock_level: Optional[int] = None
    unit: Optional[str] = None
    stock_location: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    notes: Optional[str] = None


class ReceiveStock(BaseModel):
    quantity: int
    unit_cost: Optional[Decimal] = None
    reason: str = "Поступление на склад"


class WriteOffStock(BaseModel):
    quantity: int
    reason: WriteOffReason
    description: str = ""


class ReplaceStock(BaseModel):
    quantity: int
    work_order_id: UUID


class SparePartMovementResponse(BaseModel):
    id: UUID
    spare_part_id: UUID
    quantity_delta: int
    reason: str
    work_order_id: Optional[UUID]
    write_off_reason: Optional[WriteOffReason]
    performed_by: Optional[UUID]
    unit_cost: Optional[Decimal]
    created_at: datetime

    model_config = {"from_attributes": True}


class SparePartResponse(BaseModel):
    id: UUID
    equipment_id: UUID
    name: str
    part_number: str
    quantity: int
    min_stock_level: int
    unit: str
    stock_location: Optional[str]
    unit_cost: Optional[Decimal]
    notes: Optional[str]
    status: SparePartStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Purchase Request ──────────────────────────────────────────────────────────

class PurchaseRequestCreate(BaseModel):
    spare_part_id: UUID
    quantity_needed: int
    reason: str


class PurchaseRequestReject(BaseModel):
    reason: str


class PurchaseRequestOrder(BaseModel):
    external_reference: Optional[str] = None


class PurchaseRequestResponse(BaseModel):
    id: UUID
    spare_part_id: UUID
    requested_by: UUID
    quantity_needed: int
    reason: str
    status: PurchaseRequestStatus
    approved_by: Optional[UUID]
    rejected_reason: Optional[str]
    supplier: Optional[str]
    estimated_cost: Optional[Decimal]
    external_reference: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
