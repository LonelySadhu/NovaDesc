from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from .value_objects import UserRole


@dataclass
class User:
    username: str
    email: str
    full_name: str
    role: UserRole
    hashed_password: str
    is_active: bool = True
    department_id: Optional[UUID] = None  # ссылка на сущность Department
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def deactivate(self) -> None:
        self.is_active = False

    def change_role(self, new_role: UserRole) -> None:
        self.role = new_role

    def assign_to_department(self, department_id: UUID) -> None:
        self.department_id = department_id

    @property
    def can_create_work_order(self) -> bool:
        """dispatcher и выше могут создавать наряд-заказы."""
        return self.role in (
            UserRole.DISPATCHER,
            UserRole.ENGINEER,
            UserRole.MANAGER,
            UserRole.ADMIN,
        )

    @property
    def can_view_photos(self) -> bool:
        """Фото работ доступны руководителям и выше."""
        return self.role in (UserRole.MANAGER, UserRole.ADMIN)

    @property
    def can_complete_work_order(self) -> bool:
        """Завершить наряд-заказ может инженер и выше."""
        return self.role in (UserRole.ENGINEER, UserRole.MANAGER, UserRole.ADMIN)

    @property
    def can_set_equipment_fault(self) -> bool:
        """Fault выставляется инженерным персоналом."""
        return self.role in (UserRole.ENGINEER, UserRole.MANAGER, UserRole.ADMIN)
