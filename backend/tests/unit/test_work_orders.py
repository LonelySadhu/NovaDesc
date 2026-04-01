"""Unit tests for work_orders domain entities."""
import pytest
from uuid import uuid4

from domain.work_orders.entities import WorkOrder, WorkOrderLog, WorkOrderPhoto
from domain.work_orders.value_objects import WorkOrderPriority, WorkOrderStatus, WorkOrderType


@pytest.fixture
def open_order():
    return WorkOrder(
        title="Replace filter",
        description="Replace air filter",
        equipment_id=uuid4(),
        created_by=uuid4(),
        order_type=WorkOrderType.PREVENTIVE,
    )


@pytest.fixture
def in_progress_order(open_order):
    open_order.assign(uuid4())
    return open_order


def _add_photo(order: WorkOrder) -> WorkOrderPhoto:
    return order.add_photo(
        uploaded_by=uuid4(),
        file_path="photos/test.jpg",
        original_filename="test.jpg",
        file_size=1024,
    )


# ── Initial state ─────────────────────────────────────────────────────────────

def test_new_order_status_open(open_order):
    assert open_order.status == WorkOrderStatus.OPEN
    assert open_order.priority == WorkOrderPriority.MEDIUM


def test_new_order_has_no_photos(open_order):
    assert open_order.photos == []


def test_new_order_total_hours_zero(open_order):
    assert open_order.total_hours == 0.0


# ── assign ────────────────────────────────────────────────────────────────────

def test_assign_sets_in_progress(open_order):
    tech = uuid4()
    open_order.assign(tech)
    assert open_order.status == WorkOrderStatus.IN_PROGRESS
    assert open_order.assigned_to == tech


def test_assign_on_hold_order(open_order):
    open_order.assign(uuid4())
    open_order.put_on_hold("Waiting for part")
    open_order.assign(uuid4())
    assert open_order.status == WorkOrderStatus.IN_PROGRESS


def test_cannot_assign_completed_order(in_progress_order):
    _add_photo(in_progress_order)
    in_progress_order.complete()
    with pytest.raises(ValueError):
        in_progress_order.assign(uuid4())


def test_cannot_assign_cancelled_order(open_order):
    open_order.cancel("Wrong equipment")
    with pytest.raises(ValueError):
        open_order.assign(uuid4())


# ── put_on_hold ───────────────────────────────────────────────────────────────

def test_put_on_hold(in_progress_order):
    in_progress_order.put_on_hold("Waiting for spare part")
    assert in_progress_order.status == WorkOrderStatus.ON_HOLD
    assert in_progress_order.on_hold_reason == "Waiting for spare part"


def test_put_on_hold_requires_reason(in_progress_order):
    with pytest.raises(ValueError):
        in_progress_order.put_on_hold("")


def test_cannot_put_open_order_on_hold(open_order):
    with pytest.raises(ValueError):
        open_order.put_on_hold("reason")


# ── complete ──────────────────────────────────────────────────────────────────

def test_complete_requires_photo(in_progress_order):
    with pytest.raises(ValueError, match="photo"):
        in_progress_order.complete()


def test_complete_with_photo(in_progress_order):
    _add_photo(in_progress_order)
    in_progress_order.complete()
    assert in_progress_order.status == WorkOrderStatus.COMPLETED
    assert in_progress_order.completed_at is not None


def test_cannot_complete_open_order(open_order):
    with pytest.raises(ValueError):
        open_order.complete()


# ── cancel ────────────────────────────────────────────────────────────────────

def test_cancel_open_order(open_order):
    open_order.cancel("Duplicate request")
    assert open_order.status == WorkOrderStatus.CANCELLED
    assert open_order.cancellation_reason == "Duplicate request"


def test_cancel_requires_reason(open_order):
    with pytest.raises(ValueError):
        open_order.cancel("")


def test_cannot_cancel_completed_order(in_progress_order):
    _add_photo(in_progress_order)
    in_progress_order.complete()
    with pytest.raises(ValueError):
        in_progress_order.cancel("too late")


def test_cannot_cancel_already_cancelled(open_order):
    open_order.cancel("first cancel")
    with pytest.raises(ValueError):
        open_order.cancel("second cancel")


# ── add_photo ─────────────────────────────────────────────────────────────────

def test_add_photo_increases_count(in_progress_order):
    _add_photo(in_progress_order)
    assert len(in_progress_order.photos) == 1


def test_add_multiple_photos(in_progress_order):
    _add_photo(in_progress_order)
    _add_photo(in_progress_order)
    assert len(in_progress_order.photos) == 2


def test_cannot_add_photo_to_completed_order(in_progress_order):
    _add_photo(in_progress_order)
    in_progress_order.complete()
    with pytest.raises(ValueError):
        _add_photo(in_progress_order)


def test_cannot_add_photo_to_cancelled_order(open_order):
    open_order.cancel("reason")
    with pytest.raises(ValueError):
        _add_photo(open_order)


# ── add_log ───────────────────────────────────────────────────────────────────

def test_add_log_accumulates_hours(in_progress_order):
    in_progress_order.add_log(author_id=uuid4(), message="Step 1", hours_spent=1.5)
    in_progress_order.add_log(author_id=uuid4(), message="Step 2", hours_spent=2.0)
    assert in_progress_order.total_hours == pytest.approx(3.5)
