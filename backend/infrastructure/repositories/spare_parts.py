from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from domain.spare_parts.entities import PurchaseRequest, SparePart, SparePartMovement
from domain.spare_parts.repositories import PurchaseRequestRepository, SparePartRepository
from domain.spare_parts.value_objects import (
    PurchaseRequestStatus,
    SparePartStatus,
    WriteOffReason,
)
from infrastructure.database.models.spare_parts import (
    PurchaseRequestModel,
    SparePartModel,
    SparePartMovementModel,
)


class SqlSparePartRepository(SparePartRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, spare_part_id: UUID) -> Optional[SparePart]:
        result = await self._session.execute(
            select(SparePartModel)
            .where(SparePartModel.id == spare_part_id)
            .options(selectinload(SparePartModel.movements))
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def list_by_equipment(self, equipment_id: UUID) -> List[SparePart]:
        result = await self._session.execute(
            select(SparePartModel)
            .where(SparePartModel.equipment_id == equipment_id)
            .options(selectinload(SparePartModel.movements))
        )
        return [self._to_entity(row) for row in result.scalars()]

    async def list_low_stock(self) -> List[SparePart]:
        result = await self._session.execute(
            select(SparePartModel)
            .where(
                SparePartModel.status.in_([
                    SparePartStatus.LOW_STOCK.value,
                    SparePartStatus.OUT_OF_STOCK.value,
                ])
            )
            .options(selectinload(SparePartModel.movements))
        )
        return [self._to_entity(row) for row in result.scalars()]

    async def save(self, spare_part: SparePart) -> None:
        row = await self._session.get(SparePartModel, spare_part.id)
        if row is None:
            row = SparePartModel(
                id=spare_part.id,
                equipment_id=spare_part.equipment_id,
                name=spare_part.name,
                part_number=spare_part.part_number,
                quantity=spare_part.quantity,
                min_stock_level=spare_part.min_stock_level,
                unit=spare_part.unit,
                stock_location=spare_part.stock_location,
                unit_cost=float(spare_part.unit_cost) if spare_part.unit_cost is not None else None,
                notes=spare_part.notes,
                status=spare_part.status.value,
                created_at=spare_part.created_at,
            )
            self._session.add(row)
        else:
            row.equipment_id = spare_part.equipment_id
            row.name = spare_part.name
            row.part_number = spare_part.part_number
            row.quantity = spare_part.quantity
            row.min_stock_level = spare_part.min_stock_level
            row.unit = spare_part.unit
            row.stock_location = spare_part.stock_location
            row.unit_cost = float(spare_part.unit_cost) if spare_part.unit_cost is not None else None
            row.notes = spare_part.notes
            row.status = spare_part.status.value
        await self._session.flush()

    async def save_movement(self, movement: SparePartMovement) -> None:
        existing = await self._session.get(SparePartMovementModel, movement.id)
        if existing is None:
            row = SparePartMovementModel(
                id=movement.id,
                spare_part_id=movement.spare_part_id,
                quantity_delta=movement.quantity_delta,
                reason=movement.reason,
                work_order_id=movement.work_order_id,
                write_off_reason=movement.write_off_reason.value if movement.write_off_reason else None,
                performed_by=movement.performed_by,
                unit_cost=float(movement.unit_cost) if movement.unit_cost is not None else None,
                created_at=movement.created_at,
            )
            self._session.add(row)
            await self._session.flush()

    @staticmethod
    def _to_entity(row: SparePartModel) -> SparePart:
        movements = [
            SparePartMovement(
                id=m.id,
                spare_part_id=m.spare_part_id,
                quantity_delta=m.quantity_delta,
                reason=m.reason,
                work_order_id=m.work_order_id,
                write_off_reason=WriteOffReason(m.write_off_reason) if m.write_off_reason else None,
                performed_by=m.performed_by,
                unit_cost=Decimal(str(m.unit_cost)) if m.unit_cost is not None else None,
                created_at=m.created_at,
            )
            for m in row.movements
        ]
        return SparePart(
            id=row.id,
            equipment_id=row.equipment_id,
            name=row.name,
            part_number=row.part_number,
            quantity=row.quantity,
            min_stock_level=row.min_stock_level,
            unit=row.unit,
            stock_location=row.stock_location,
            unit_cost=Decimal(str(row.unit_cost)) if row.unit_cost is not None else None,
            notes=row.notes,
            status=SparePartStatus(row.status),
            movements=movements,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class SqlPurchaseRequestRepository(PurchaseRequestRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, request_id: UUID) -> Optional[PurchaseRequest]:
        row = await self._session.get(PurchaseRequestModel, request_id)
        return self._to_entity(row) if row else None

    async def list_by_status(self, status: PurchaseRequestStatus) -> List[PurchaseRequest]:
        result = await self._session.execute(
            select(PurchaseRequestModel).where(PurchaseRequestModel.status == status.value)
        )
        return [self._to_entity(row) for row in result.scalars()]

    async def list_by_spare_part(self, spare_part_id: UUID) -> List[PurchaseRequest]:
        result = await self._session.execute(
            select(PurchaseRequestModel).where(
                PurchaseRequestModel.spare_part_id == spare_part_id
            )
        )
        return [self._to_entity(row) for row in result.scalars()]

    async def save(self, request: PurchaseRequest) -> None:
        row = await self._session.get(PurchaseRequestModel, request.id)
        if row is None:
            row = PurchaseRequestModel(
                id=request.id,
                spare_part_id=request.spare_part_id,
                requested_by=request.requested_by,
                quantity_needed=request.quantity_needed,
                reason=request.reason,
                status=request.status.value,
                approved_by=request.approved_by,
                rejected_reason=request.rejected_reason,
                supplier=request.supplier,
                estimated_cost=float(request.estimated_cost) if request.estimated_cost is not None else None,
                external_reference=request.external_reference,
                created_at=request.created_at,
            )
            self._session.add(row)
        else:
            row.spare_part_id = request.spare_part_id
            row.quantity_needed = request.quantity_needed
            row.reason = request.reason
            row.status = request.status.value
            row.approved_by = request.approved_by
            row.rejected_reason = request.rejected_reason
            row.supplier = request.supplier
            row.estimated_cost = float(request.estimated_cost) if request.estimated_cost is not None else None
            row.external_reference = request.external_reference
        await self._session.flush()

    @staticmethod
    def _to_entity(row: PurchaseRequestModel) -> PurchaseRequest:
        return PurchaseRequest(
            id=row.id,
            spare_part_id=row.spare_part_id,
            requested_by=row.requested_by,
            quantity_needed=row.quantity_needed,
            reason=row.reason,
            status=PurchaseRequestStatus(row.status),
            approved_by=row.approved_by,
            rejected_reason=row.rejected_reason,
            supplier=row.supplier,
            estimated_cost=Decimal(str(row.estimated_cost)) if row.estimated_cost is not None else None,
            external_reference=row.external_reference,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
