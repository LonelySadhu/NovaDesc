from datetime import datetime
from typing import List, Optional
from uuid import UUID

from domain.work_orders.entities import WorkOrder, WorkOrderLog, WorkOrderPhoto
from domain.work_orders.repositories import WorkOrderRepository
from domain.work_orders.value_objects import WorkOrderPriority, WorkOrderStatus, WorkOrderType


class WorkOrderService:
    def __init__(self, repo: WorkOrderRepository) -> None:
        self._repo = repo

    async def create(
        self,
        title: str,
        description: str,
        equipment_id: UUID,
        created_by: UUID,
        order_type: WorkOrderType,
        priority: WorkOrderPriority = WorkOrderPriority.MEDIUM,
        assigned_to: Optional[UUID] = None,
        due_date: Optional[datetime] = None,
    ) -> WorkOrder:
        order = WorkOrder(
            title=title,
            description=description,
            equipment_id=equipment_id,
            created_by=created_by,
            order_type=order_type,
            priority=priority,
            due_date=due_date,
        )
        if assigned_to:
            order.assign(assigned_to)
        await self._repo.save(order)
        return order

    async def assign(self, work_order_id: UUID, technician_id: UUID) -> WorkOrder:
        order = await self._get_or_404(work_order_id)
        order.assign(technician_id)
        await self._repo.save(order)
        return order

    async def put_on_hold(self, work_order_id: UUID, reason: str) -> WorkOrder:
        order = await self._get_or_404(work_order_id)
        order.put_on_hold(reason)
        await self._repo.save(order)
        return order

    async def complete(self, work_order_id: UUID) -> WorkOrder:
        order = await self._get_or_404(work_order_id)
        order.complete()
        await self._repo.save(order)
        return order

    async def cancel(self, work_order_id: UUID, reason: str) -> WorkOrder:
        order = await self._get_or_404(work_order_id)
        order.cancel(reason)
        await self._repo.save(order)
        return order

    async def add_log(
        self,
        work_order_id: UUID,
        author_id: UUID,
        message: str,
        hours_spent: float = 0.0,
    ) -> WorkOrderLog:
        order = await self._get_or_404(work_order_id)
        log = order.add_log(author_id=author_id, message=message, hours_spent=hours_spent)
        await self._repo.save_log(log)
        return log

    async def add_photo(
        self,
        work_order_id: UUID,
        uploaded_by: UUID,
        file_path: str,
        original_filename: str,
        file_size: int,
        caption: Optional[str] = None,
    ) -> WorkOrderPhoto:
        order = await self._get_or_404(work_order_id)
        photo = order.add_photo(
            uploaded_by=uploaded_by,
            file_path=file_path,
            original_filename=original_filename,
            file_size=file_size,
            caption=caption,
        )
        await self._repo.save_photo(photo)
        return photo

    async def _get_or_404(self, work_order_id: UUID) -> WorkOrder:
        order = await self._repo.get_by_id(work_order_id)
        if order is None:
            raise ValueError(f"WorkOrder {work_order_id} not found")
        return order
