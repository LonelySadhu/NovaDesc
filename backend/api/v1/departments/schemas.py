from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    head_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    head_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None


class DepartmentResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    head_id: Optional[UUID]
    parent_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
