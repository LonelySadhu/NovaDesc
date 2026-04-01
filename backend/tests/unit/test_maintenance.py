"""Unit tests for maintenance domain entities."""
from datetime import datetime, timedelta
import pytest
from uuid import uuid4

from domain.equipment.value_objects import MaintenanceInterval, MaintenanceIntervalUnit
from domain.maintenance.entities import MaintenanceSchedule


@pytest.fixture
def daily_schedule():
    return MaintenanceSchedule(
        equipment_id=uuid4(),
        title="Daily inspection",
        description="Check oil level",
        interval_value=1,
        interval_unit=MaintenanceIntervalUnit.DAYS,
    )


@pytest.fixture
def monthly_schedule():
    return MaintenanceSchedule(
        equipment_id=uuid4(),
        title="Monthly service",
        description="Full service",
        interval_value=1,
        interval_unit=MaintenanceIntervalUnit.MONTHS,
    )


@pytest.fixture
def cycle_schedule():
    return MaintenanceSchedule(
        equipment_id=uuid4(),
        title="Cycle-based check",
        description="Check after N cycles",
        interval_value=500,
        interval_unit=MaintenanceIntervalUnit.CYCLES,
    )


# ── Validation ────────────────────────────────────────────────────────────────

def test_zero_interval_raises():
    with pytest.raises(ValueError):
        MaintenanceSchedule(
            equipment_id=uuid4(),
            title="Bad",
            description="Bad",
            interval_value=0,
            interval_unit=MaintenanceIntervalUnit.DAYS,
        )


def test_negative_interval_raises():
    with pytest.raises(ValueError):
        MaintenanceSchedule(
            equipment_id=uuid4(),
            title="Bad",
            description="Bad",
            interval_value=-1,
            interval_unit=MaintenanceIntervalUnit.HOURS,
        )


# ── interval_hours ────────────────────────────────────────────────────────────

def test_interval_hours_for_days(daily_schedule):
    assert daily_schedule.interval_hours == pytest.approx(24.0)


def test_interval_hours_for_months(monthly_schedule):
    assert monthly_schedule.interval_hours == pytest.approx(730.0)


def test_interval_hours_for_cycles_is_none(cycle_schedule):
    assert cycle_schedule.interval_hours is None


# ── is_overdue ────────────────────────────────────────────────────────────────

def test_not_overdue_when_next_due_is_none(daily_schedule):
    assert daily_schedule.is_overdue is False


def test_not_overdue_when_next_due_in_future(daily_schedule):
    daily_schedule.next_due_at = datetime.utcnow() + timedelta(hours=1)
    assert daily_schedule.is_overdue is False


def test_is_overdue_when_next_due_in_past(daily_schedule):
    daily_schedule.next_due_at = datetime.utcnow() - timedelta(hours=1)
    assert daily_schedule.is_overdue is True


# ── record_completion ─────────────────────────────────────────────────────────

def test_record_completion_sets_last_performed(daily_schedule):
    performed = datetime(2026, 1, 1, 10, 0)
    daily_schedule.record_completion(performed)
    assert daily_schedule.last_performed_at == performed


def test_record_completion_calculates_next_due_days(daily_schedule):
    performed = datetime(2026, 1, 1, 10, 0)
    daily_schedule.record_completion(performed)
    expected = performed + timedelta(days=1)
    assert daily_schedule.next_due_at == expected


def test_record_completion_calculates_next_due_hours():
    schedule = MaintenanceSchedule(
        equipment_id=uuid4(),
        title="Hourly check",
        description="Check",
        interval_value=8,
        interval_unit=MaintenanceIntervalUnit.HOURS,
    )
    performed = datetime(2026, 1, 1, 8, 0)
    schedule.record_completion(performed)
    assert schedule.next_due_at == performed + timedelta(hours=8)


def test_record_completion_calculates_next_due_months(monthly_schedule):
    performed = datetime(2026, 1, 1)
    monthly_schedule.record_completion(performed)
    assert monthly_schedule.next_due_at == pytest.approx(
        performed + timedelta(days=30.4167), abs=timedelta(seconds=1)
    )


def test_record_completion_clears_overdue(daily_schedule):
    daily_schedule.next_due_at = datetime.utcnow() - timedelta(days=10)
    assert daily_schedule.is_overdue is True
    daily_schedule.record_completion(datetime.utcnow())
    assert daily_schedule.is_overdue is False


# ── is_compliant_with ─────────────────────────────────────────────────────────

def test_compliant_when_plan_equals_normative():
    schedule = MaintenanceSchedule(
        equipment_id=uuid4(), title="T", description="D",
        interval_value=30, interval_unit=MaintenanceIntervalUnit.DAYS,
    )
    normative = MaintenanceInterval(value=30, unit=MaintenanceIntervalUnit.DAYS)
    assert schedule.is_compliant_with(normative) is True


def test_compliant_when_plan_shorter_than_normative():
    schedule = MaintenanceSchedule(
        equipment_id=uuid4(), title="T", description="D",
        interval_value=25, interval_unit=MaintenanceIntervalUnit.DAYS,
    )
    normative = MaintenanceInterval(value=30, unit=MaintenanceIntervalUnit.DAYS)
    assert schedule.is_compliant_with(normative) is True


def test_not_compliant_when_plan_exceeds_normative():
    schedule = MaintenanceSchedule(
        equipment_id=uuid4(), title="T", description="D",
        interval_value=60, interval_unit=MaintenanceIntervalUnit.DAYS,
    )
    normative = MaintenanceInterval(value=30, unit=MaintenanceIntervalUnit.DAYS)
    assert schedule.is_compliant_with(normative) is False


def test_compliant_within_5_percent_tolerance():
    # 31 дней против норматива 30 — в пределах 5% допуска (31/30 = 1.033)
    schedule = MaintenanceSchedule(
        equipment_id=uuid4(), title="T", description="D",
        interval_value=31, interval_unit=MaintenanceIntervalUnit.DAYS,
    )
    normative = MaintenanceInterval(value=30, unit=MaintenanceIntervalUnit.DAYS)
    assert schedule.is_compliant_with(normative) is True


def test_compliant_when_cycles_vs_hours():
    """Cycles нельзя сравнить с часами — считается compliant."""
    schedule = MaintenanceSchedule(
        equipment_id=uuid4(), title="T", description="D",
        interval_value=500, interval_unit=MaintenanceIntervalUnit.CYCLES,
    )
    normative = MaintenanceInterval(value=30, unit=MaintenanceIntervalUnit.DAYS)
    assert schedule.is_compliant_with(normative) is True