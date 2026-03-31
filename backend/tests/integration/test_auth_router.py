"""
Integration tests for /api/v1/auth/* endpoints.

Uses httpx.AsyncClient with FastAPI dependency overrides —
no real database required.
"""
import pytest
from httpx import AsyncClient, ASGITransport

from application.users.service import AuthService
from core.dependencies import get_auth_service, get_current_user
from domain.users.entities import User
from infrastructure.auth.jwt import create_access_token, create_refresh_token
from main import app
from tests.conftest import InMemoryUserRepository


# ── Helpers ───────────────────────────────────────────────────────────────────

@pytest.fixture
def repo(admin_user: User) -> InMemoryUserRepository:
    return InMemoryUserRepository(users=[admin_user])


@pytest.fixture
def auth_service(repo: InMemoryUserRepository) -> AuthService:
    return AuthService(repo)


@pytest.fixture
def client(auth_service: AuthService, admin_user: User):
    """AsyncClient with dependency overrides (no real DB)."""
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    app.dependency_overrides[get_current_user] = lambda: admin_user
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()


# ── POST /auth/login ──────────────────────────────────────────────────────────

async def test_login_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "secret123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "bad"})
    assert resp.status_code == 401


async def test_login_unknown_user(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={"username": "ghost", "password": "x"})
    assert resp.status_code == 401


async def test_login_missing_fields(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={"username": "admin"})
    assert resp.status_code == 422


# ── POST /auth/refresh ────────────────────────────────────────────────────────

async def test_refresh_success(client: AsyncClient, admin_user: User):
    refresh_token = create_refresh_token(admin_user.id)
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_refresh_with_access_token_fails(client: AsyncClient, admin_user: User):
    """Sending an access token to /refresh must be rejected."""
    access_token = create_access_token(admin_user.id, admin_user.role.value)
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401


async def test_refresh_invalid_token(client: AsyncClient):
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": "garbage"})
    assert resp.status_code == 401


# ── GET /auth/me ──────────────────────────────────────────────────────────────

async def test_me_returns_current_user(client: AsyncClient, admin_user: User):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == admin_user.username
    assert body["role"] == admin_user.role.value
    assert body["is_active"] is True


async def test_me_without_token_fails():
    """No override for get_current_user — real bearer check runs."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        resp = await c.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)  # HTTPBearer: 403 no header, 401 invalid token
