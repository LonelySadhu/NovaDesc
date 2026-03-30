from __future__ import annotations

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
class WorkOrderPhoto:
    """
    Фото выполненных работ — обязательное условие для завершения наряд-заказа.
    Доступны для просмотра руководителям подразделений и выше.
    """
    work_order_id: UUID
    uploaded_by: UUID            # user_id
    file_path: str               # путь/ключ в хранилище (S3, локально)
    original_filename: str
    file_size: int               # в байтах
    caption: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    uploaded_at: datetime = field(default_factory=datetime.utcnow)


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
    on_hold_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    logs: List[WorkOrderLog] = field(default_factory=list)
    photos: List[WorkOrderPhoto] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def assign(self, technician_id: UUID) -> None:
        if self.status not in (WorkOrderStatus.OPEN, WorkOrderStatus.ON_HOLD):
            raise ValueError("Can only assign open or on-hold orders")
        self.assigned_to = technician_id
        self.status = WorkOrderStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def put_on_hold(self, reason: str) -> None:
        if self.status != WorkOrderStatus.IN_PROGRESS:
            raise ValueError("Only in-progress orders can be put on hold")
        if not reason or not reason.strip():
            raise ValueError("Hold reason is required")
        self.on_hold_reason = reason.strip()
        self.status = WorkOrderStatus.ON_HOLD
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """
        Завершение наряд-заказа.
        Требует наличия хотя бы одного фото выполненных работ.
        """
        if self.status != WorkOrderStatus.IN_PROGRESS:
            raise ValueError("Only in-progress orders can be completed")
        if not self.photos:
            raise ValueError(
                "Cannot complete work order without at least one photo of completed work"
            )
        self.status = WorkOrderStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def cancel(self, reason: str) -> None:
        if self.status in (WorkOrderStatus.COMPLETED, WorkOrderStatus.CANCELLED):
            raise ValueError("Cannot cancel a completed or already cancelled order")
        if not reason or not reason.strip():
            raise ValueError("Cancellation reason is required")
        self.cancellation_reason = reason.strip()
        self.status = WorkOrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def add_photo(
        self,
        uploaded_by: UUID,
        file_path: str,
        original_filename: str,
        file_size: int,
        caption: Optional[str] = None,
    ) -> WorkOrderPhoto:
        """Добавить фото выполненных работ."""
        if self.status == WorkOrderStatus.COMPLETED:
            raise ValueError("Cannot add photos to a completed work order")
        if self.status == WorkOrderStatus.CANCELLED:
            raise ValueError("Cannot add photos to a cancelled work order")
        photo = WorkOrderPhoto(
            work_order_id=self.id,
            uploaded_by=uploaded_by,
            file_path=file_path,
            original_filename=original_filename,
            file_size=file_size,
            caption=caption,
        )
        self.photos.append(photo)
        self.updated_at = datetime.utcnow()
        return photo

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