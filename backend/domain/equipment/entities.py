from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from .value_objects import (
    EquipmentStatus,
    MaintenanceInterval,
    SerialNumber,
    SystemStatus,
)


@dataclass
class EquipmentSystem:
    """
    Система оборудования (например, «Система кондиционирования»).
    Является верхним уровнем иерархии: Система → Оборудование → Компоненты.
    Принадлежит подразделению (department), имеет ответственного (stakeholder).
    """
    name: str
    department_id: UUID
    description: Optional[str] = None
    system_type: Optional[str] = None       # e.g. "HVAC", "Power", "Fire Safety"
    # Ответственный руководитель/инженер из подразделения
    stakeholder_id: Optional[UUID] = None
    status: SystemStatus = SystemStatus.ACTIVE
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def decommission(self) -> None:
        self.status = SystemStatus.DECOMMISSIONED
        self.updated_at = datetime.utcnow()

    def set_stakeholder(self, user_id: UUID) -> None:
        self.stakeholder_id = user_id
        self.updated_at = datetime.utcnow()


@dataclass
class Equipment:
    """
    Единица оборудования — принадлежит EquipmentSystem.
    maintenance_interval — нормативный интервал ТО из документации.
    """
    name: str
    serial_number: SerialNumber
    manufacturer: str
    model: str
    location: str
    system_id: UUID                          # обязательная принадлежность системе
    status: EquipmentStatus = EquipmentStatus.ACTIVE
    maintenance_interval: Optional[MaintenanceInterval] = None
    installed_at: Optional[datetime] = None
    # Теги/характеристики для AI-поиска
    metadata: dict = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def decommission(self) -> None:
        self.status = EquipmentStatus.DECOMMISSIONED
        self.updated_at = datetime.utcnow()

    def set_under_maintenance(self) -> None:
        if self.status == EquipmentStatus.DECOMMISSIONED:
            raise ValueError("Decommissioned equipment cannot be set under maintenance")
        self.status = EquipmentStatus.UNDER_MAINTENANCE
        self.updated_at = datetime.utcnow()

    def restore(self) -> None:
        """Вернуть в рабочее состояние (из under_maintenance или fault)."""
        if self.status == EquipmentStatus.DECOMMISSIONED:
            raise ValueError("Decommissioned equipment cannot be restored")
        self.status = EquipmentStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def set_fault(self) -> None:
        """Выставить аварийный статус вручную инженерным персоналом."""
        if self.status == EquipmentStatus.DECOMMISSIONED:
            raise ValueError("Decommissioned equipment cannot be set to fault")
        self.status = EquipmentStatus.FAULT
        self.updated_at = datetime.utcnow()
