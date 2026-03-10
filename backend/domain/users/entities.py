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
    department: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def deactivate(self) -> None:
        self.is_active = False

    def change_role(self, new_role: UserRole) -> None:
        self.role = new_role
