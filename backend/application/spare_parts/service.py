from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from domain.spare_parts.entities import PurchaseRequest, SparePart, SparePartMovement
from domain.spare_parts.repositories import PurchaseRequestRepository, SparePartRepository
from domain.spare_parts.value_objects import WriteOffReason


class SparePartService:
    def __init__(self, repo: SparePartRepository) -> None:
        self._repo = repo

    async def create(
        self,
        equipment_id: UUID,
        name: str,
        part_number: str,
        min_stock_level: int = 0,
        unit: str = "шт.",
        stock_location: Optional[str] = None,
        unit_cost: Optional[Decimal] = None,
        notes: Optional[str] = None,
    ) -> SparePart:
        part = SparePart(
            equipment_id=equipment_id,
            name=name,
            part_number=part_number,
            min_stock_level=min_stock_level,
            unit=unit,
            stock_location=stock_location,
            unit_cost=unit_cost,
            notes=notes,
        )
        await self._repo.save(part)
        return part

    async def receive(
        self,
        spare_part_id: UUID,
        quantity: int,
        performed_by: UUID,
        unit_cost: Optional[Decimal] = None,
        reason: str = "Поступление на склад",
    ) -> SparePartMovement:
        part = await self._get_or_404(spare_part_id)
        movement = part.receive(
            quantity=quantity,
            performed_by=performed_by,
            unit_cost=unit_cost,
            reason=reason,
        )
        await self._repo.save(part)
        await self._repo.save_movement(movement)
        return movement

    async def write_off(
        self,
        spare_part_id: UUID,
        quantity: int,
        reason: WriteOffReason,
        performed_by: UUID,
        description: str = "",
    ) -> SparePartMovement:
        part = await self._get_or_404(spare_part_id)
        movement = part.write_off(
            quantity=quantity,
            reason=reason,
            performed_by=performed_by,
            description=description,
        )
        await self._repo.save(part)
        await self._repo.save_movement(movement)
        return movement

    async def replace(
        self,
        spare_part_id: UUID,
        quantity: int,
        work_order_id: UUID,
        performed_by: UUID,
    ) -> SparePartMovement:
        part = await self._get_or_404(spare_part_id)
        movement = part.replace(
            quantity=quantity,
            work_order_id=work_order_id,
            performed_by=performed_by,
        )
        await self._repo.save(part)
        await self._repo.save_movement(movement)
        return movement

    async def _get_or_404(self, spare_part_id: UUID) -> SparePart:
        part = await self._repo.get_by_id(spare_part_id)
        if part is None:
            raise ValueError(f"SparePart {spare_part_id} not found")
        return part


class PurchaseRequestService:
    def __init__(self, repo: PurchaseRequestRepository) -> None:
        self._repo = repo

    async def create(
        self,
        spare_part_id: UUID,
        requested_by: UUID,
        quantity_needed: int,
        reason: str,
    ) -> PurchaseRequest:
        request = PurchaseRequest(
            spare_part_id=spare_part_id,
            requested_by=requested_by,
            quantity_needed=quantity_needed,
            reason=reason,
        )
        await self._repo.save(request)
        return request

    async def submit(self, request_id: UUID) -> PurchaseRequest:
        req = await self._get_or_404(request_id)
        req.submit()
        await self._repo.save(req)
        return req

    async def approve(self, request_id: UUID, approved_by: UUID) -> PurchaseRequest:
        req = await self._get_or_404(request_id)
        req.approve(approved_by)
        await self._repo.save(req)
        return req

    async def reject(self, request_id: UUID, reason: str) -> PurchaseRequest:
        req = await self._get_or_404(request_id)
        req.reject(reason)
        await self._repo.save(req)
        return req

    async def mark_ordered(
        self, request_id: UUID, external_reference: Optional[str] = None
    ) -> PurchaseRequest:
        req = await self._get_or_404(request_id)
        req.mark_ordered(external_reference)
        await self._repo.save(req)
        return req

    async def mark_received(self, request_id: UUID) -> PurchaseRequest:
        req = await self._get_or_404(request_id)
        req.mark_received()
        await self._repo.save(req)
        return req

    async def _get_or_404(self, request_id: UUID) -> PurchaseRequest:
        req = await self._repo.get_by_id(request_id)
        if req is None:
            raise ValueError(f"PurchaseRequest {request_id} not found")
        return req
