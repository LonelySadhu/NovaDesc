from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EquipmentStatus(str, Enum):
    ACTIVE = "active"
    UNDER_MAINTENANCE = "under_maintenance"
    DECOMMISSIONED = "decommissioned"
    FAULT = "fault"


class SystemStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECOMMISSIONED = "decommissioned"


class MaintenanceIntervalUnit(str, Enum):
    HOURS = "hours"
    DAYS = "days"
    MONTHS = "months"
    CYCLES = "cycles"

    def to_hours_multiplier(self) -> float:
        return {
            MaintenanceIntervalUnit.HOURS: 1.0,
            MaintenanceIntervalUnit.DAYS: 24.0,
            MaintenanceIntervalUnit.MONTHS: 730.0,   # 365 * 24 / 12
            MaintenanceIntervalUnit.CYCLES: 0.0,     # cycles не переводятся в часы
        }[self]


@dataclass(frozen=True)
class SerialNumber:
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Serial number cannot be empty")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class MaintenanceInterval:
    """Нормативный интервал ТО из документации на оборудование."""
    value: int
    unit: MaintenanceIntervalUnit

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Maintenance interval must be positive")

    def to_hours(self) -> Optional[float]:
        """Перевод в часы. None для cycles (не конвертируемо)."""
        multiplier = self.unit.to_hours_multiplier()
        if multiplier == 0.0:
            return None
        return self.value * multiplier
