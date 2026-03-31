"""Shared fixtures for all tests."""
import sys
import os

# Ensure backend/ is on the path so imports work without installing the package
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

import pytest

from domain.users.entities import User
from domain.users.repositories import UserRepository
from domain.users.value_objects import UserRole
from infrastructure.auth.password import hash_password


# ── In-memory UserRepository for tests ───────────────────────────────────────

class InMemoryUserRepository(UserRepository):
    def __init__(self, users: List[User] = None):
        self._users: List[User] = list(users or [])

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return next((u for u in self._users if u.id == user_id), None)

    async def get_by_username(self, username: str) -> Optional[User]:
        return next((u for u in self._users if u.username == username), None)

    async def get_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._users if u.email == email), None)

    async def list(self, limit: int = 100, offset: int = 0) -> List[User]:
        return self._users[offset : offset + limit]

    async def save(self, user: User) -> User:
        self._users = [u for u in self._users if u.id != user.id]
        self._users.append(user)
        return user


# ── Common fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def admin_user() -> User:
    return User(
        id=uuid4(),
        username="admin",
        email="admin@test.local",
        full_name="Test Admin",
        role=UserRole.ADMIN,
        hashed_password=hash_password("secret123"),
        is_active=True,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def user_repo(admin_user: User) -> InMemoryUserRepository:
    return InMemoryUserRepository(users=[admin_user])
