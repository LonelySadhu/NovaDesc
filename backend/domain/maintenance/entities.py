from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from domain.equipment.value_objects import MaintenanceInterval, MaintenanceIntervalUnit


@dataclass
class MaintenanceSchedule:
    """
    Реальный план ТО для конкретного оборудования, управляемый людьми.

    interval_value + interval_unit задаются пользователем; система хранит
    interval_hours для сквозного сравнения с нормативом (Equipment.maintenance_interval).

    Если нормативный интервал (из документации) не совпадает с реальным планом —
    is_compliant_with() вернёт False и система покажет предупреждение.
    """
    equipment_id: UUID
    title: str
    description: str
    interval_value: int
    interval_unit: MaintenanceIntervalUnit
    last_performed_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.interval_value <= 0:
            raise ValueError("Interval value must be positive")

    @property
    def interval_hours(self) -> Optional[float]:
        """Интервал в часах для сравнения с нормативом. None для cycles."""
        multiplier = self.interval_unit.to_hours_multiplier()
        if multiplier == 0.0:
            return None
        return self.interval_value * multiplier

    def record_completion(self, performed_at: datetime) -> None:
        """Зафиксировать выполнение ТО и пересчитать следующую дату."""
        self.last_performed_at = performed_at
        self.next_due_at = self._calculate_next_due(performed_at)
        self.updated_at = datetime.utcnow()

    def _calculate_next_due(self, from_date: datetime) -> datetime:
        if self.interval_unit == MaintenanceIntervalUnit.DAYS:
            return from_date + timedelta(days=self.interval_value)
        elif self.interval_unit == MaintenanceIntervalUnit.HOURS:
            return from_date + timedelta(hours=self.interval_value)
        elif self.interval_unit == MaintenanceIntervalUnit.MONTHS:
            # Простой расчёт: +30.4 дня на месяц
            return from_date + timedelta(days=self.interval_value * 30.4167)
        else:
            # CYCLES — не можем вычислить дату, возвращаем from_date как placeholder
            return from_date

    @property
    def is_overdue(self) -> bool:
        if self.next_due_at is None:
            return False
        return datetime.utcnow() > self.next_due_at

    def is_compliant_with(self, normative: MaintenanceInterval) -> bool:
        """
        Проверить, соответствует ли реальный план нормативному интервалу из документации.
        Сравниваем через часы. Если одна из единиц CYCLES — сравнение невозможно (True).
        """
        plan_hours = self.interval_hours
        norm_hours = normative.to_hours()
        if plan_hours is None or norm_hours is None:
            # Нет смысла сравнивать cycles с часами/днями
            return True
        # Допуск 5% — незначительное расхождение из-за округлений
        return plan_hours <= norm_hours * 1.05
