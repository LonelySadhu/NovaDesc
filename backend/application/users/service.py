from uuid import UUID

from domain.users.entities import User
from domain.users.repositories import UserRepository
from infrastructure.auth.password import verify_password
from infrastructure.auth.jwt import create_access_token, create_refresh_token


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def login(self, username: str, password: str) -> dict:
        user = await self._repo.get_by_username(username)
        if user is None or not user.is_active:
            raise ValueError("Invalid credentials")
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        return {
            "access_token": create_access_token(user.id, user.role.value),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer",
        }

    async def get_by_id(self, user_id: UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        return user