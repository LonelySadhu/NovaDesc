"""Integration tests for /api/v1/work-orders/* endpoints."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient, ASGITransport

from core.dependencies import get_current_user, get_storage, get_work_order_repo
from domain.storage.ports import StoragePort
from domain.users.entities import User
from domain.users.value_objects import UserRole
from domain.work_orders.entities import WorkOrder, WorkOrderLog, WorkOrderPhoto
from domain.work_orders.repositories import WorkOrderRepository
from domain.work_orders.value_objects import WorkOrderPriority, WorkOrderStatus
from infrastructure.auth.password import hash_password
from main import app


# ── Fake storage ──────────────────────────────────────────────────────────────

class FakeStoragePort(StoragePort):
    def __init__(self):
        self.uploads: dict[tuple, bytes] = {}

    async def upload(self, bucket, key, data, content_type="application/octet-stream"):
        self.uploads[(bucket, key)] = data
        return key

    async def delete(self, bucket, key):
        self.uploads.pop((bucket, key), None)

    def presigned_url(self, bucket, key, expires_seconds=3600):
        return f"http://fake-minio/{bucket}/{key}"


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
def fake_storage():
    return FakeStoragePort()


@pytest.fixture
def dispatcher():
    return _make_user(UserRole.DISPATCHER)


@pytest.fixture
def engineer():
    return _make_user(UserRole.ENGINEER)


@pytest.fixture
def client_dispatcher(wo_repo, dispatcher, fake_storage):
    app.dependency_overrides[get_work_order_repo] = lambda: wo_repo
    app.dependency_overrides[get_current_user] = lambda: dispatcher
    app.dependency_overrides[get_storage] = lambda: fake_storage
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()


@pytest.fixture
def client_engineer(wo_repo, engineer, fake_storage):
    app.dependency_overrides[get_work_order_repo] = lambda: wo_repo
    app.dependency_overrides[get_current_user] = lambda: engineer
    app.dependency_overrides[get_storage] = lambda: fake_storage
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
    # загружаем фото через multipart
    resp = await client_engineer.post(
        f"/api/v1/work-orders/{order.id}/photos",
        files={"file": ("photo.jpg", b"\xff\xd8\xff" + b"x" * 100, "image/jpeg")},
    )
    assert resp.status_code == 201
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


# ── Photos ────────────────────────────────────────────────────────────────────

_FAKE_JPEG = b"\xff\xd8\xff" + b"x" * 200  # minimal fake JPEG bytes


def _make_order_in_repo(wo_repo, order_type_str="corrective"):
    from domain.work_orders.entities import WorkOrder
    from domain.work_orders.value_objects import WorkOrderType
    type_map = {
        "corrective": WorkOrderType.CORRECTIVE,
        "preventive": WorkOrderType.PREVENTIVE,
    }
    return WorkOrder(
        title="T", description="D", equipment_id=uuid4(),
        created_by=uuid4(), order_type=type_map[order_type_str],
    )


async def test_upload_photo_returns_201_and_presigned_url(client_engineer, wo_repo, fake_storage):
    order = _make_order_in_repo(wo_repo)
    await wo_repo.save(order)

    resp = await client_engineer.post(
        f"/api/v1/work-orders/{order.id}/photos",
        files={"file": ("shot.jpg", _FAKE_JPEG, "image/jpeg")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["original_filename"] == "shot.jpg"
    assert body["file_size"] == len(_FAKE_JPEG)
    assert body["url"] is not None
    assert "fake-minio" in body["url"]


async def test_upload_photo_stores_file_in_storage(client_engineer, wo_repo, fake_storage):
    order = _make_order_in_repo(wo_repo)
    await wo_repo.save(order)

    await client_engineer.post(
        f"/api/v1/work-orders/{order.id}/photos",
        files={"file": ("img.png", _FAKE_JPEG, "image/png")},
    )
    # FakeStorage должен содержать ровно один объект в нужном bucket
    keys = [k for (b, k) in fake_storage.uploads if b == "novadesc-media"]
    assert len(keys) == 1
    assert str(order.id) in keys[0]


async def test_upload_photo_rejects_non_image(client_engineer, wo_repo):
    order = _make_order_in_repo(wo_repo)
    await wo_repo.save(order)

    resp = await client_engineer.post(
        f"/api/v1/work-orders/{order.id}/photos",
        files={"file": ("doc.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert resp.status_code == 415


async def test_upload_photo_with_caption(client_engineer, wo_repo):
    order = _make_order_in_repo(wo_repo)
    await wo_repo.save(order)

    resp = await client_engineer.post(
        f"/api/v1/work-orders/{order.id}/photos",
        files={"file": ("shot.jpg", _FAKE_JPEG, "image/jpeg")},
        data={"caption": "Before repair"},
    )
    assert resp.status_code == 201
    assert resp.json()["caption"] == "Before repair"


async def test_list_photos_returns_presigned_urls(client_engineer, wo_repo, fake_storage):
    order = _make_order_in_repo(wo_repo)
    await wo_repo.save(order)
    # загружаем два фото
    for i in range(2):
        await client_engineer.post(
            f"/api/v1/work-orders/{order.id}/photos",
            files={"file": (f"photo{i}.jpg", _FAKE_JPEG, "image/jpeg")},
        )

    resp = await client_engineer.get(f"/api/v1/work-orders/{order.id}/photos")
    assert resp.status_code == 200
    photos = resp.json()
    assert len(photos) == 2
    assert all(p["url"] is not None for p in photos)
