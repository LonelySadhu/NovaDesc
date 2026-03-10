from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from .value_objects import WorkOrderStatus, WorkOrderPriority, WorkOrderType


@dataclass
class WorkOrderLog:
    work_order_id: UUID
    author_id: UUID
    message: str
    hours_spent: float = 0.0
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkOrder:
    title: str
    description: str
    equipment_id: UUID
    created_by: UUID
    order_type: WorkOrderType
    priority: WorkOrderPriority = WorkOrderPriority.MEDIUM
    status: WorkOrderStatus = WorkOrderStatus.OPEN
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    logs: List[WorkOrderLog] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def assign(self, technician_id: UUID) -> None:
        self.assigned_to = technician_id
        self.status = WorkOrderStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        if self.status != WorkOrderStatus.IN_PROGRESS:
            raise ValueError("Only in-progress orders can be completed")
        self.status = WorkOrderStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_log(self, author_id: UUID, message: str, hours_spent: float = 0.0) -> WorkOrderLog:
        log = WorkOrderLog(
            work_order_id=self.id,
            author_id=author_id,
            message=message,
            hours_spent=hours_spent,
        )
        self.logs.append(log)
        self.updated_at = datetime.utcnow()
        return log

    @property
    def total_hours(self) -> float:
        return sum(log.hours_spent for log in self.logs)
