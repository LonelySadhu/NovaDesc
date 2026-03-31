import pytest

from application.users.service import AuthService
from domain.users.entities import User
from domain.users.value_objects import UserRole
from infrastructure.auth.jwt import decode_token
from infrastructure.auth.password import hash_password
from tests.conftest import InMemoryUserRepository


@pytest.fixture
def service(user_repo: InMemoryUserRepository) -> AuthService:
    return AuthService(user_repo)


async def test_login_returns_tokens(service: AuthService):
    result = await service.login("admin", "secret123")

    assert "access_token" in result
    assert "refresh_token" in result
    assert result["token_type"] == "bearer"


async def test_login_access_token_contains_role(service: AuthService):
    result = await service.login("admin", "secret123")
    payload = decode_token(result["access_token"])

    assert payload["role"] == UserRole.ADMIN.value
    assert payload["type"] == "access"


async def test_login_wrong_password_raises(service: AuthService):
    with pytest.raises(ValueError, match="Invalid credentials"):
        await service.login("admin", "wrongpassword")


async def test_login_unknown_user_raises(service: AuthService):
    with pytest.raises(ValueError, match="Invalid credentials"):
        await service.login("nobody", "secret123")


async def test_login_inactive_user_raises(admin_user: User, user_repo: InMemoryUserRepository):
    admin_user.deactivate()
    await user_repo.save(admin_user)
    service = AuthService(user_repo)

    with pytest.raises(ValueError, match="Invalid credentials"):
        await service.login("admin", "secret123")


async def test_get_by_id_returns_user(service: AuthService, admin_user: User):
    user = await service.get_by_id(admin_user.id)
    assert user.username == "admin"


async def test_get_by_id_unknown_raises(service: AuthService):
    from uuid import uuid4
    with pytest.raises(ValueError, match="User not found"):
        await service.get_by_id(uuid4())
