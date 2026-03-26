from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class MaintenanceSchedule:
    equipment_id: UUID
    title: str
    description: str
    interval_days: int
    last_performed_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def record_completion(self, performed_at: datetime) -> None:
        from datetime import timedelta
        self.last_performed_at = performed_at
        self.next_due_at = performed_at + timedelta(days=self.interval_days)

    @property
    def is_overdue(self) -> bool:
        if self.next_due_at is None:
            return False
        return datetime.utcnow() > self.next_due_at
