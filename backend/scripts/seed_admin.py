"""
Seed script: creates the initial admin user if it doesn't exist.

Usage (from backend/ directory):
    python -m scripts.seed_admin
    # or with custom credentials via env:
    ADMIN_USERNAME=admin ADMIN_PASSWORD=secret python -m scripts.seed_admin
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings
from domain.users.entities import User
from domain.users.value_objects import UserRole
from infrastructure.auth.password import hash_password
from infrastructure.users.repository import SqlUserRepository

ADMIN_USERNAME = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASS", "changeme123")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@novadesc.local")
ADMIN_FULL_NAME = os.getenv("ADMIN_FULL_NAME", "System Administrator")


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        repo = SqlUserRepository(session)
        existing = await repo.get_by_username(ADMIN_USERNAME)
        if existing:
            existing.hashed_password = hash_password(ADMIN_PASSWORD)
            await repo.save(existing)
            await session.commit()
            print(f"[seed] User '{ADMIN_USERNAME}' already exists — password updated.")
            return

        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            full_name=ADMIN_FULL_NAME,
            role=UserRole.ADMIN,
            hashed_password=hash_password(ADMIN_PASSWORD),
        )
        await repo.save(admin)
        await session.commit()
        print(f"[seed] Admin user '{ADMIN_USERNAME}' created successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())