"""Unit tests for spare_parts domain entities."""
from decimal import Decimal
import pytest
from uuid import uuid4

from domain.spare_parts.entities import PurchaseRequest, SparePart
from domain.spare_parts.value_objects import (
    PurchaseRequestStatus,
    SparePartStatus,
    WriteOffReason,
)


@pytest.fixture
def part():
    return SparePart(
        equipment_id=uuid4(),
        name="Air Filter",
        part_number="AF-100",
        min_stock_level=2,
    )


@pytest.fixture
def stocked_part(part):
    part.receive(quantity=10, performed_by=uuid4())
    return part


# ── Initial state ─────────────────────────────────────────────────────────────

def test_new_part_out_of_stock(part):
    assert part.status == SparePartStatus.OUT_OF_STOCK
    assert part.quantity == 0


# ── receive ───────────────────────────────────────────────────────────────────

def test_receive_increases_quantity(part):
    part.receive(quantity=5, performed_by=uuid4())
    assert part.quantity == 5


def test_receive_updates_status_in_stock(part):
    part.receive(quantity=10, performed_by=uuid4())
    assert part.status == SparePartStatus.IN_STOCK


def test_receive_updates_status_low_stock(part):
    part.receive(quantity=1, performed_by=uuid4())  # min_stock_level=2
    assert part.status == SparePartStatus.LOW_STOCK


def test_receive_creates_movement(part):
    part.receive(quantity=5, performed_by=uuid4())
    assert len(part.movements) == 1
    assert part.movements[0].quantity_delta == 5


def test_receive_zero_raises(part):
    with pytest.raises(ValueError):
        part.receive(quantity=0, performed_by=uuid4())


def test_receive_negative_raises(part):
    with pytest.raises(ValueError):
        part.receive(quantity=-1, performed_by=uuid4())


# ── write_off ─────────────────────────────────────────────────────────────────

def test_write_off_decreases_quantity(stocked_part):
    stocked_part.write_off(quantity=3, reason=WriteOffReason.DEFECT, performed_by=uuid4())
    assert stocked_part.quantity == 7


def test_write_off_creates_negative_movement(stocked_part):
    stocked_part.write_off(quantity=3, reason=WriteOffReason.DEFECT, performed_by=uuid4())
    movement = stocked_part.movements[-1]
    assert movement.quantity_delta == -3
    assert movement.write_off_reason == WriteOffReason.DEFECT


def test_write_off_more_than_stock_raises(stocked_part):
    with pytest.raises(ValueError):
        stocked_part.write_off(quantity=100, reason=WriteOffReason.DEFECT, performed_by=uuid4())


def test_write_off_to_zero_sets_out_of_stock(stocked_part):
    stocked_part.write_off(quantity=10, reason=WriteOffReason.EXPIRED, performed_by=uuid4())
    assert stocked_part.status == SparePartStatus.OUT_OF_STOCK


def test_write_off_to_low_stock(stocked_part):
    stocked_part.write_off(quantity=9, reason=WriteOffReason.DAMAGED, performed_by=uuid4())
    assert stocked_part.quantity == 1
    assert stocked_part.status == SparePartStatus.LOW_STOCK


# ── replace ───────────────────────────────────────────────────────────────────

def test_replace_decreases_quantity(stocked_part):
    wo_id = uuid4()
    stocked_part.replace(quantity=2, work_order_id=wo_id, performed_by=uuid4())
    assert stocked_part.quantity == 8


def test_replace_links_work_order(stocked_part):
    wo_id = uuid4()
    movement = stocked_part.replace(quantity=1, work_order_id=wo_id, performed_by=uuid4())
    assert movement.work_order_id == wo_id
    assert movement.write_off_reason == WriteOffReason.REPLACED


def test_replace_more_than_stock_raises(stocked_part):
    with pytest.raises(ValueError):
        stocked_part.replace(quantity=100, work_order_id=uuid4(), performed_by=uuid4())


# ── PurchaseRequest ───────────────────────────────────────────────────────────

@pytest.fixture
def draft_request():
    return PurchaseRequest(
        spare_part_id=uuid4(),
        requested_by=uuid4(),
        quantity_needed=5,
        reason="Stock depleted",
    )


def test_draft_request_initial_status(draft_request):
    assert draft_request.status == PurchaseRequestStatus.DRAFT


def test_submit_draft(draft_request):
    draft_request.submit()
    assert draft_request.status == PurchaseRequestStatus.SUBMITTED


def test_cannot_submit_twice(draft_request):
    draft_request.submit()
    with pytest.raises(ValueError):
        draft_request.submit()


def test_approve_submitted(draft_request):
    draft_request.submit()
    approver = uuid4()
    draft_request.approve(approver)
    assert draft_request.status == PurchaseRequestStatus.APPROVED
    assert draft_request.approved_by == approver


def test_cannot_approve_draft(draft_request):
    with pytest.raises(ValueError):
        draft_request.approve(uuid4())


def test_reject_submitted(draft_request):
    draft_request.submit()
    draft_request.reject("Budget exceeded")
    assert draft_request.status == PurchaseRequestStatus.REJECTED
    assert draft_request.rejected_reason == "Budget exceeded"


def test_reject_draft(draft_request):
    draft_request.reject("Not needed")
    assert draft_request.status == PurchaseRequestStatus.REJECTED


def test_mark_ordered(draft_request):
    draft_request.submit()
    draft_request.approve(uuid4())
    draft_request.mark_ordered("SAP-123")
    assert draft_request.status == PurchaseRequestStatus.ORDERED
    assert draft_request.external_reference == "SAP-123"


def test_cannot_order_without_approval(draft_request):
    draft_request.submit()
    with pytest.raises(ValueError):
        draft_request.mark_ordered()


def test_mark_received(draft_request):
    draft_request.submit()
    draft_request.approve(uuid4())
    draft_request.mark_ordered()
    draft_request.mark_received()
    assert draft_request.status == PurchaseRequestStatus.RECEIVED


def test_cannot_receive_if_not_ordered(draft_request):
    draft_request.submit()
    draft_request.approve(uuid4())
    with pytest.raises(ValueError):
        draft_request.mark_received()
