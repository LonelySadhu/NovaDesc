"""Unit tests for equipment domain entities."""
import pytest
from uuid import uuid4

from domain.equipment.entities import Equipment, EquipmentSystem
from domain.equipment.value_objects import (
    EquipmentStatus,
    MaintenanceInterval,
    MaintenanceIntervalUnit,
    SerialNumber,
    SystemStatus,
)


# ── SerialNumber ──────────────────────────────────────────────────────────────

def test_serial_number_value():
    sn = SerialNumber("SN-001")
    assert str(sn) == "SN-001"


def test_serial_number_empty_raises():
    with pytest.raises(ValueError):
        SerialNumber("")


def test_serial_number_whitespace_raises():
    with pytest.raises(ValueError):
        SerialNumber("   ")


# ── MaintenanceInterval ───────────────────────────────────────────────────────

def test_interval_to_hours_days():
    mi = MaintenanceInterval(value=7, unit=MaintenanceIntervalUnit.DAYS)
    assert mi.to_hours() == pytest.approx(168.0)


def test_interval_to_hours_months():
    mi = MaintenanceInterval(value=1, unit=MaintenanceIntervalUnit.MONTHS)
    assert mi.to_hours() == pytest.approx(730.0)


def test_interval_to_hours_cycles_is_none():
    mi = MaintenanceInterval(value=100, unit=MaintenanceIntervalUnit.CYCLES)
    assert mi.to_hours() is None


def test_interval_zero_raises():
    with pytest.raises(ValueError):
        MaintenanceInterval(value=0, unit=MaintenanceIntervalUnit.DAYS)


def test_interval_negative_raises():
    with pytest.raises(ValueError):
        MaintenanceInterval(value=-5, unit=MaintenanceIntervalUnit.HOURS)


# ── EquipmentSystem ───────────────────────────────────────────────────────────

@pytest.fixture
def system():
    return EquipmentSystem(name="HVAC", department_id=uuid4())


def test_system_default_status_active(system):
    assert system.status == SystemStatus.ACTIVE


def test_system_decommission(system):
    system.decommission()
    assert system.status == SystemStatus.DECOMMISSIONED


def test_system_set_stakeholder(system):
    user_id = uuid4()
    system.set_stakeholder(user_id)
    assert system.stakeholder_id == user_id


# ── Equipment ─────────────────────────────────────────────────────────────────

@pytest.fixture
def equipment():
    return Equipment(
        name="Chiller",
        serial_number=SerialNumber("CH-001"),
        manufacturer="Trane",
        model="CGAM",
        location="Room 1",
        system_id=uuid4(),
    )


def test_equipment_default_status_active(equipment):
    assert equipment.status == EquipmentStatus.ACTIVE


def test_equipment_set_under_maintenance(equipment):
    equipment.set_under_maintenance()
    assert equipment.status == EquipmentStatus.UNDER_MAINTENANCE


def test_equipment_restore_from_maintenance(equipment):
    equipment.set_under_maintenance()
    equipment.restore()
    assert equipment.status == EquipmentStatus.ACTIVE


def test_equipment_set_fault(equipment):
    equipment.set_fault()
    assert equipment.status == EquipmentStatus.FAULT


def test_equipment_restore_from_fault(equipment):
    equipment.set_fault()
    equipment.restore()
    assert equipment.status == EquipmentStatus.ACTIVE


def test_equipment_decommission(equipment):
    equipment.decommission()
    assert equipment.status == EquipmentStatus.DECOMMISSIONED


def test_decommissioned_cannot_set_under_maintenance(equipment):
    equipment.decommission()
    with pytest.raises(ValueError):
        equipment.set_under_maintenance()


def test_decommissioned_cannot_restore(equipment):
    equipment.decommission()
    with pytest.raises(ValueError):
        equipment.restore()


def test_decommissioned_cannot_set_fault(equipment):
    equipment.decommission()
    with pytest.raises(ValueError):
        equipment.set_fault()
