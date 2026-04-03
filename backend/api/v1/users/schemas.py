from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from domain.users.value_objects import UserRole


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: UserRole
    department_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    department_id: Optional[UUID] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    department_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}
