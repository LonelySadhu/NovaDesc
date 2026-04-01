from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from domain.work_orders.entities import WorkOrder, WorkOrderLog, WorkOrderPhoto
from domain.work_orders.repositories import WorkOrderRepository
from domain.work_orders.value_objects import WorkOrderPriority, WorkOrderStatus, WorkOrderType
from infrastructure.database.models.work_orders import (
    WorkOrderLogModel,
    WorkOrderModel,
    WorkOrderPhotoModel,
)


class SqlWorkOrderRepository(WorkOrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, work_order_id: UUID) -> Optional[WorkOrder]:
        result = await self._session.execute(
            select(WorkOrderModel)
            .where(WorkOrderModel.id == work_order_id)
            .options(
                selectinload(WorkOrderModel.logs),
                selectinload(WorkOrderModel.photos),
            )
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def list(
        self,
        equipment_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
        status: Optional[WorkOrderStatus] = None,
        priority: Optional[WorkOrderPriority] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[WorkOrder]:
        stmt = (
            select(WorkOrderModel)
            .options(
                selectinload(WorkOrderModel.logs),
                selectinload(WorkOrderModel.photos),
            )
        )
        if equipment_id is not None:
            stmt = stmt.where(WorkOrderModel.equipment_id == equipment_id)
        if assigned_to is not None:
            stmt = stmt.where(WorkOrderModel.assigned_to == assigned_to)
        if status is not None:
            stmt = stmt.where(WorkOrderModel.status == status.value)
        if priority is not None:
            stmt = stmt.where(WorkOrderModel.priority == priority.value)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars()]

    async def save(self, work_order: WorkOrder) -> None:
        row = await self._session.get(WorkOrderModel, work_order.id)
        if row is None:
            row = WorkOrderModel(
                id=work_order.id,
                title=work_order.title,
                description=work_order.description,
                equipment_id=work_order.equipment_id,
                created_by=work_order.created_by,
                order_type=work_order.order_type.value,
                priority=work_order.priority.value,
                status=work_order.status.value,
                assigned_to=work_order.assigned_to,
                due_date=work_order.due_date,
                completed_at=work_order.completed_at,
                on_hold_reason=work_order.on_hold_reason,
                cancellation_reason=work_order.cancellation_reason,
                created_at=work_order.created_at,
            )
            self._session.add(row)
        else:
            row.title = work_order.title
            row.description = work_order.description
            row.equipment_id = work_order.equipment_id
            row.order_type = work_order.order_type.value
            row.priority = work_order.priority.value
            row.status = work_order.status.value
            row.assigned_to = work_order.assigned_to
            row.due_date = work_order.due_date
            row.completed_at = work_order.completed_at
            row.on_hold_reason = work_order.on_hold_reason
            row.cancellation_reason = work_order.cancellation_reason
        await self._session.flush()

    async def delete(self, work_order_id: UUID) -> None:
        row = await self._session.get(WorkOrderModel, work_order_id)
        if row:
            await self._session.delete(row)
            await self._session.flush()

    async def save_photo(self, photo: WorkOrderPhoto) -> None:
        existing = await self._session.get(WorkOrderPhotoModel, photo.id)
        if existing is None:
            row = WorkOrderPhotoModel(
                id=photo.id,
                work_order_id=photo.work_order_id,
                uploaded_by=photo.uploaded_by,
                file_path=photo.file_path,
                original_filename=photo.original_filename,
                file_size=photo.file_size,
                caption=photo.caption,
                uploaded_at=photo.uploaded_at,
            )
            self._session.add(row)
            await self._session.flush()

    async def list_photos(self, work_order_id: UUID) -> List[WorkOrderPhoto]:
        result = await self._session.execute(
            select(WorkOrderPhotoModel).where(
                WorkOrderPhotoModel.work_order_id == work_order_id
            )
        )
        return [self._photo_to_entity(row) for row in result.scalars()]

    @staticmethod
    def _to_entity(row: WorkOrderModel) -> WorkOrder:
        logs = [
            WorkOrderLog(
                id=log.id,
                work_order_id=log.work_order_id,
                author_id=log.author_id,
                message=log.message,
                hours_spent=log.hours_spent,
                created_at=log.created_at,
            )
            for log in row.logs
        ]
        photos = [
            WorkOrderPhoto(
                id=photo.id,
                work_order_id=photo.work_order_id,
                uploaded_by=photo.uploaded_by,
                file_path=photo.file_path,
                original_filename=photo.original_filename,
                file_size=photo.file_size,
                caption=photo.caption,
                uploaded_at=photo.uploaded_at,
            )
            for photo in row.photos
        ]
        return WorkOrder(
            id=row.id,
            title=row.title,
            description=row.description,
            equipment_id=row.equipment_id,
            created_by=row.created_by,
            order_type=WorkOrderType(row.order_type),
            priority=WorkOrderPriority(row.priority),
            status=WorkOrderStatus(row.status),
            assigned_to=row.assigned_to,
            due_date=row.due_date,
            completed_at=row.completed_at,
            on_hold_reason=row.on_hold_reason,
            cancellation_reason=row.cancellation_reason,
            logs=logs,
            photos=photos,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _photo_to_entity(row: WorkOrderPhotoModel) -> WorkOrderPhoto:
        return WorkOrderPhoto(
            id=row.id,
            work_order_id=row.work_order_id,
            uploaded_by=row.uploaded_by,
            file_path=row.file_path,
            original_filename=row.original_filename,
            file_size=row.file_size,
            caption=row.caption,
            uploaded_at=row.uploaded_at,
        )
