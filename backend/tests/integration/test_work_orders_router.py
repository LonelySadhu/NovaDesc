"""Integration tests for /api/v1/work-orders/* endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient, ASGITransport

from core.dependencies import get_current_user, get_work_order_repo
from domain.users.entities import User
from domain.users.value_objects import UserRole
from domain.work_orders.entities import WorkOrder, WorkOrderLog, WorkOrderPhoto
from domain.work_orders.repositories import WorkOrderRepository
from domain.work_orders.value_objects import WorkOrderPriority, WorkOrderStatus
from infrastructure.auth.password import hash_password
from main import app


# ── In-memory WorkOrder repository ───────────────────────────────────────────

class InMemoryWorkOrderRepository(WorkOrderRepository):
    def __init__(self):
        self._orders: dict[UUID, WorkOrder] = {}
        self._logs: list[WorkOrderLog] = []
        self._photos: list[WorkOrderPhoto] = []

    async def get_by_id(self, work_order_id: UUID) -> Optional[WorkOrder]:
        return self._orders.get(work_order_id)

    async def list(self, equipment_id=None, assigned_to=None, status=None,
                   priority=None, limit=100, offset=0) -> List[WorkOrder]:
        items = list(self._orders.values())
        if equipment_id:
            items = [o for o in items if o.equipment_id == equipment_id]
        if assigned_to:
            items = [o for o in items if o.assigned_to == assigned_to]
        if status:
            items = [o for o in items if o.status == status]
        if priority:
            items = [o for o in items if o.priority == priority]
        return items[offset:offset + limit]

    async def save(self, work_order: WorkOrder) -> None:
        self._orders[work_order.id] = work_order

    async def delete(self, work_order_id: UUID) -> None:
        self._orders.pop(work_order_id, None)

    async def save_log(self, log: WorkOrderLog) -> None:
        self._logs.append(log)

    async def list_logs(self, work_order_id: UUID) -> List[WorkOrderLog]:
        return [l for l in self._logs if l.work_order_id == work_order_id]

    async def save_photo(self, photo: WorkOrderPhoto) -> None:
        self._photos.append(photo)

    async def list_photos(self, work_order_id: UUID) -> List[WorkOrderPhoto]:
        return [p for p in self._photos if p.work_order_id == work_order_id]


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_user(role: UserRole) -> User:
    return User(
        id=uuid4(), username=role.value, email=f"{role.value}@test.local",
        full_name=role.value.title(), role=role,
        hashed_password=hash_password("x"), is_active=True,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def wo_repo():
    return InMemoryWorkOrderRepository()


@pytest.fixture
def dispatcher():
    return _make_user(UserRole.DISPATCHER)


@pytest.fixture
def engineer():
    return _make_user(UserRole.ENGINEER)


@pytest.fixture
def client_dispatcher(wo_repo, dispatcher):
    app.dependency_overrides[get_work_order_repo] = lambda: wo_repo
    app.dependency_overrides[get_current_user] = lambda: dispatcher
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()


@pytest.fixture
def client_engineer(wo_repo, engineer):
    app.dependency_overrides[get_work_order_repo] = lambda: wo_repo
    app.dependency_overrides[get_current_user] = lambda: engineer
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()


_WO_PAYLOAD = {
    "title": "Replace filter",
    "description": "Air filter replacement",
    "equipment_id": str(uuid4()),
    "order_type": "preventive",
}


# ── Create ────────────────────────────────────────────────────────────────────

async def test_create_work_order(client_dispatcher):
    resp = await client_dispatcher.post("/api/v1/work-orders/", json=_WO_PAYLOAD)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "open"
    assert body["title"] == "Replace filter"


async def test_technician_cannot_create(wo_repo):
    tech = _make_user(UserRole.TECHNICIAN)
    app.dependency_overrides[get_work_order_repo] = lambda: wo_repo
    app.dependency_overrides[get_current_user] = lambda: tech
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        resp = await c.post("/api/v1/work-orders/", json=_WO_PAYLOAD)
    app.dependency_overrides.clear()
    assert resp.status_code == 403


# ── Get / List ────────────────────────────────────────────────────────────────

async def test_get_work_order(client_dispatcher, wo_repo):
    from domain.work_orders.entities import WorkOrder
    from domain.work_orders.value_objects import WorkOrderType
    order = WorkOrder(
        title="Check pump", description="desc", equipment_id=uuid4(),
        created_by=uuid4(), order_type=WorkOrderType.INSPECTION,
    )
    await wo_repo.save(order)
    resp = await client_dispatcher.get(f"/api/v1/work-orders/{order.id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Check pump"


async def test_get_not_found(client_dispatcher):
    resp = await client_dispatcher.get(f"/api/v1/work-orders/{uuid4()}")
    assert resp.status_code == 404


# ── State machine ─────────────────────────────────────────────────────────────

async def test_assign(client_dispatcher, wo_repo, dispatcher):
    resp = await client_dispatcher.post("/api/v1/work-orders/", json=_WO_PAYLOAD)
    wo_id = resp.json()["id"]
    tech_id = str(uuid4())
    resp = await client_dispatcher.post(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"technician_id": tech_id},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"
    assert resp.json()["assigned_to"] == tech_id


async def test_put_on_hold(client_engineer, wo_repo):
    from domain.work_orders.entities import WorkOrder
    from domain.work_orders.value_objects import WorkOrderType
    order = WorkOrder(
        title="T", description="D", equipment_id=uuid4(),
        created_by=uuid4(), order_type=WorkOrderType.CORRECTIVE,
    )
    order.assign(uuid4())
    await wo_repo.save(order)
    resp = await client_engineer.post(
        f"/api/v1/work-orders/{order.id}/hold",
        json={"reason": "Waiting for part"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "on_hold"


async def test_complete_requires_photo(client_engineer, wo_repo):
    from domain.work_orders.entities import WorkOrder
    from domain.work_orders.value_objects import WorkOrderType
    order = WorkOrder(
        title="T", description="D", equipment_id=uuid4(),
        created_by=uuid4(), order_type=WorkOrderType.CORRECTIVE,
    )
    order.assign(uuid4())
    await wo_repo.save(order)
    resp = await client_engineer.post(f"/api/v1/work-orders/{order.id}/complete")
    assert resp.status_code == 400


async def test_complete_with_photo(client_engineer, wo_repo, engineer):
    from domain.work_orders.entities import WorkOrder
    from domain.work_orders.value_objects import WorkOrderType
    order = WorkOrder(
        title="T", description="D", equipment_id=uuid4(),
        created_by=uuid4(), order_type=WorkOrderType.CORRECTIVE,
    )
    order.assign(uuid4())
    await wo_repo.save(order)
    # add photo
    await client_engineer.post(
        f"/api/v1/work-orders/{order.id}/photos",
        json={"file_path": "p.jpg", "original_filename": "p.jpg", "file_size": 100},
    )
    # reload order from repo so photos list is populated
    saved = wo_repo._orders[order.id]
    saved.photos = [p for p in wo_repo._photos if p.work_order_id == order.id]
    resp = await client_engineer.post(f"/api/v1/work-orders/{order.id}/complete")
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


async def test_cancel(client_dispatcher, wo_repo):
    resp = await client_dispatcher.post("/api/v1/work-orders/", json=_WO_PAYLOAD)
    wo_id = resp.json()["id"]
    resp = await client_dispatcher.post(
        f"/api/v1/work-orders/{wo_id}/cancel",
        json={"reason": "Duplicate"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_cancel_requires_reason(client_dispatcher, wo_repo):
    resp = await client_dispatcher.post("/api/v1/work-orders/", json=_WO_PAYLOAD)
    wo_id = resp.json()["id"]
    resp = await client_dispatcher.post(
        f"/api/v1/work-orders/{wo_id}/cancel",
        json={"reason": ""},
    )
    assert resp.status_code == 400


# ── Logs ──────────────────────────────────────────────────────────────────────

async def test_add_log(client_engineer, wo_repo):
    from domain.work_orders.entities import WorkOrder
    from domain.work_orders.value_objects import WorkOrderType
    order = WorkOrder(
        title="T", description="D", equipment_id=uuid4(),
        created_by=uuid4(), order_type=WorkOrderType.PREVENTIVE,
    )
    await wo_repo.save(order)
    resp = await client_engineer.post(
        f"/api/v1/work-orders/{order.id}/logs",
        json={"message": "Started work", "hours_spent": 1.5},
    )
    assert resp.status_code == 201
    assert resp.json()["hours_spent"] == 1.5
