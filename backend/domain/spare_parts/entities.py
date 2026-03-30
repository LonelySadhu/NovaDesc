from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from .value_objects import PurchaseRequestStatus, SparePartStatus, WriteOffReason


@dataclass
class SparePartMovement:
    """
    Проводка движения запчасти (журнал): поступление, списание, замена.
    Иммутабельная запись — не изменяется после создания.
    """
    spare_part_id: UUID
    quantity_delta: int          # >0 поступление, <0 расход
    reason: str
    work_order_id: Optional[UUID] = None   # ссылка на наряд-заказ (при замене)
    write_off_reason: Optional[WriteOffReason] = None
    performed_by: Optional[UUID] = None    # user_id
    unit_cost: Optional[Decimal] = None    # стоимость единицы на момент проводки
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SparePart:
    """
    Запчасть/расходный материал, относящийся к конкретному оборудованию.
    Ведёт количественный учёт через движения (SparePartMovement).
    """
    equipment_id: UUID
    name: str
    part_number: str             # каталожный номер
    quantity: int = 0            # текущий остаток на складе
    min_stock_level: int = 0     # порог для LOW_STOCK warning
    unit: str = "шт."           # единица измерения
    stock_location: Optional[str] = None   # место хранения (склад, ячейка)
    unit_cost: Optional[Decimal] = None    # средняя стоимость единицы
    notes: Optional[str] = None
    status: SparePartStatus = SparePartStatus.OUT_OF_STOCK
    movements: List[SparePartMovement] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def _recalculate_status(self) -> None:
        if self.quantity <= 0:
            self.status = SparePartStatus.OUT_OF_STOCK
        elif self.quantity <= self.min_stock_level:
            self.status = SparePartStatus.LOW_STOCK
        else:
            self.status = SparePartStatus.IN_STOCK

    def receive(
        self,
        quantity: int,
        performed_by: UUID,
        unit_cost: Optional[Decimal] = None,
        reason: str = "Поступление на склад",
    ) -> SparePartMovement:
        """Оприходование запчасти на склад."""
        if quantity <= 0:
            raise ValueError("Receive quantity must be positive")
        movement = SparePartMovement(
            spare_part_id=self.id,
            quantity_delta=quantity,
            reason=reason,
            performed_by=performed_by,
            unit_cost=unit_cost or self.unit_cost,
        )
        self.quantity += quantity
        self.movements.append(movement)
        self._recalculate_status()
        self.updated_at = datetime.utcnow()
        return movement

    def write_off(
        self,
        quantity: int,
        reason: WriteOffReason,
        performed_by: UUID,
        description: str = "",
    ) -> SparePartMovement:
        """Списание по браку, несоответствию или истечению срока."""
        if quantity <= 0:
            raise ValueError("Write-off quantity must be positive")
        if quantity > self.quantity:
            raise ValueError(f"Cannot write off {quantity}: only {self.quantity} in stock")
        movement = SparePartMovement(
            spare_part_id=self.id,
            quantity_delta=-quantity,
            reason=description or reason.value,
            write_off_reason=reason,
            performed_by=performed_by,
        )
        self.quantity -= quantity
        self.movements.append(movement)
        self._recalculate_status()
        self.updated_at = datetime.utcnow()
        return movement

    def replace(
        self,
        quantity: int,
        work_order_id: UUID,
        performed_by: UUID,
    ) -> SparePartMovement:
        """Списание при замене в ходе выполнения наряд-заказа."""
        if quantity <= 0:
            raise ValueError("Replace quantity must be positive")
        if quantity > self.quantity:
            raise ValueError(f"Cannot use {quantity}: only {self.quantity} in stock")
        movement = SparePartMovement(
            spare_part_id=self.id,
            quantity_delta=-quantity,
            reason="Замена по наряд-заказу",
            work_order_id=work_order_id,
            write_off_reason=WriteOffReason.REPLACED,
            performed_by=performed_by,
        )
        self.quantity -= quantity
        self.movements.append(movement)
        self._recalculate_status()
        self.updated_at = datetime.utcnow()
        return movement


@dataclass
class PurchaseRequest:
    """
    Заявка на закупку запчасти. Может выгружаться во внешние системы (SAP, 1C).
    """
    spare_part_id: UUID
    requested_by: UUID           # user_id инициатора
    quantity_needed: int
    reason: str
    status: PurchaseRequestStatus = PurchaseRequestStatus.DRAFT
    approved_by: Optional[UUID] = None
    rejected_reason: Optional[str] = None
    supplier: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    # Внешние ссылки для интеграции
    external_reference: Optional[str] = None   # номер в SAP/1C
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def submit(self) -> None:
        if self.status != PurchaseRequestStatus.DRAFT:
            raise ValueError("Only draft requests can be submitted")
        self.status = PurchaseRequestStatus.SUBMITTED
        self.updated_at = datetime.utcnow()

    def approve(self, approved_by: UUID) -> None:
        if self.status != PurchaseRequestStatus.SUBMITTED:
            raise ValueError("Only submitted requests can be approved")
        self.approved_by = approved_by
        self.status = PurchaseRequestStatus.APPROVED
        self.updated_at = datetime.utcnow()

    def reject(self, reason: str) -> None:
        if self.status not in (PurchaseRequestStatus.SUBMITTED, PurchaseRequestStatus.DRAFT):
            raise ValueError("Cannot reject request in current status")
        self.rejected_reason = reason
        self.status = PurchaseRequestStatus.REJECTED
        self.updated_at = datetime.utcnow()

    def mark_ordered(self, external_reference: Optional[str] = None) -> None:
        if self.status != PurchaseRequestStatus.APPROVED:
            raise ValueError("Only approved requests can be ordered")
        self.external_reference = external_reference
        self.status = PurchaseRequestStatus.ORDERED
        self.updated_at = datetime.utcnow()

    def mark_received(self) -> None:
        if self.status != PurchaseRequestStatus.ORDERED:
            raise ValueError("Only ordered requests can be marked received")
        self.status = PurchaseRequestStatus.RECEIVED
        self.updated_at = datetime.utcnow()
