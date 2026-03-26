from dataclasses import dataclass
from enum import Enum


class EquipmentStatus(str, Enum):
    ACTIVE = "active"
    UNDER_MAINTENANCE = "under_maintenance"
    DECOMMISSIONED = "decommissioned"
    FAULT = "fault"


class MaintenanceIntervalUnit(str, Enum):
    HOURS = "hours"
    DAYS = "days"
    MONTHS = "months"
    CYCLES = "cycles"


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
    value: int
    unit: MaintenanceIntervalUnit

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Maintenance interval must be positive")
