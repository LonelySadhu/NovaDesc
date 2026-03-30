from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base

if TYPE_CHECKING:
    from .department import DepartmentModel
    from .spare_parts import SparePartModel
    from .maintenance import MaintenanceScheduleModel
    from .work_orders import WorkOrderModel


class EquipmentSystemModel(Base):
    __tablename__ = "equipment_systems"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    system_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False
    )
    stakeholder_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    department: Mapped[DepartmentModel] = relationship("DepartmentModel", back_populates="systems")
    equipment: Mapped[List[EquipmentModel]] = relationship(
        "EquipmentModel", back_populates="system"
    )


class EquipmentModel(Base):
    __tablename__ = "equipment"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    system_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment_systems.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False, index=True)
    # Нормативный интервал ТО из документации
    maintenance_interval_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    maintenance_interval_unit: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    installed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Теги/характеристики для AI-поиска
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    system: Mapped[EquipmentSystemModel] = relationship(
        "EquipmentSystemModel", back_populates="equipment"
    )
    spare_parts: Mapped[List[SparePartModel]] = relationship(
        "SparePartModel", back_populates="equipment"
    )
    work_orders: Mapped[List[WorkOrderModel]] = relationship(
        "WorkOrderModel", back_populates="equipment"
    )
    maintenance_schedules: Mapped[List[MaintenanceScheduleModel]] = relationship(
        "MaintenanceScheduleModel", back_populates="equipment"
    )