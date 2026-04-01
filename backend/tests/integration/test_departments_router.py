"""Integration tests for /api/v1/departments/* endpoints."""
from typing import List, Optional
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient, ASGITransport

from core.dependencies import get_current_user, get_department_repo
from domain.departments.entities import Department
from domain.departments.repositories import DepartmentRepository
from domain.users.entities import User
from domain.users.value_objects import UserRole
from infrastructure.auth.password import hash_password
from main import app


# ── In-memory Department repository ──────────────────────────────────────────

class InMemoryDepartmentRepository(DepartmentRepository):
    def __init__(self):
        self._store: dict[UUID, Department] = {}

    async def get_by_id(self, department_id: UUID) -> Optional[Department]:
        return self._store.get(department_id)

    async def list_all(self, include_inactive: bool = False) -> List[Department]:
        items = list(self._store.values())
        if not include_inactive:
            items = [d for d in items if d.is_active]
        return items

    async def save(self, department: Department) -> None:
        self._store[department.id] = department

    async def delete(self, department_id: UUID) -> None:
        self._store.pop(department_id, None)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def manager_user() -> User:
    from datetime import datetime
    return User(
        id=uuid4(), username="manager", email="mgr@test.local",
        full_name="Manager", role=UserRole.MANAGER,
        hashed_password=hash_password("x"), is_active=True,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def dept_repo() -> InMemoryDepartmentRepository:
    return InMemoryDepartmentRepository()


@pytest.fixture
def client(dept_repo, manager_user):
    app.dependency_overrides[get_department_repo] = lambda: dept_repo
    app.dependency_overrides[get_current_user] = lambda: manager_user
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()


# ── Tests ─────────────────────────────────────────────────────────────────────

async def test_create_department(client):
    resp = await client.post("/api/v1/departments/", json={"name": "IT"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "IT"
    assert body["is_active"] is True


async def test_list_departments(client, dept_repo):
    dept = Department(name="Ops")
    await dept_repo.save(dept)
    resp = await client.get("/api/v1/departments/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_get_department(client, dept_repo):
    dept = Department(name="HR")
    await dept_repo.save(dept)
    resp = await client.get(f"/api/v1/departments/{dept.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "HR"


async def test_get_department_not_found(client):
    resp = await client.get(f"/api/v1/departments/{uuid4()}")
    assert resp.status_code == 404


async def test_update_department(client, dept_repo):
    dept = Department(name="Old Name")
    await dept_repo.save(dept)
    resp = await client.patch(f"/api/v1/departments/{dept.id}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


async def test_deactivate_department(client, dept_repo, manager_user):
    from domain.users.value_objects import UserRole
    from datetime import datetime
    admin = User(
        id=uuid4(), username="admin2", email="a2@test.local",
        full_name="Admin", role=UserRole.ADMIN,
        hashed_password=hash_password("x"), is_active=True,
        created_at=datetime.utcnow(),
    )
    app.dependency_overrides[get_current_user] = lambda: admin
    dept = Department(name="ToDeactivate")
    await dept_repo.save(dept)
    resp = await client.post(f"/api/v1/departments/{dept.id}/deactivate")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_list_excludes_inactive_by_default(client, dept_repo):
    active = Department(name="Active")
    inactive = Department(name="Inactive")
    inactive.deactivate()
    await dept_repo.save(active)
    await dept_repo.save(inactive)
    resp = await client.get("/api/v1/departments/")
    names = [d["name"] for d in resp.json()]
    assert "Active" in names
    assert "Inactive" not in names


async def test_list_includes_inactive_when_requested(client, dept_repo):
    active = Department(name="Active")
    inactive = Department(name="Inactive")
    inactive.deactivate()
    await dept_repo.save(active)
    await dept_repo.save(inactive)
    resp = await client.get("/api/v1/departments/?include_inactive=true")
    assert len(resp.json()) == 2
