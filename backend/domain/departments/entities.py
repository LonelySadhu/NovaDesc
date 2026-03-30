from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Department:
    """Подразделение — владеет системами оборудования, имеет своих инженеров и руководителей."""
    name: str
    description: Optional[str] = None
    # Руководитель подразделения (ссылка на User)
    head_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None  # для иерархии подразделений
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def set_head(self, user_id: UUID) -> None:
        self.head_id = user_id
        self.updated_at = datetime.utcnow()
