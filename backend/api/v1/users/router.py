from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import get_current_user, get_user_repo, require_roles
from domain.users.entities import User
from domain.users.value_objects import UserRole
from infrastructure.auth.password import hash_password
from .schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        department_id=user.department_id,
        created_at=user.created_at,
    )


@router.get("/", response_model=List[UserResponse])
async def list_users(
    repo=Depends(get_user_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    users = await repo.list(limit=500)
    return [_to_response(u) for u in users]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    repo=Depends(get_user_repo),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    existing = await repo.get_by_username(body.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    existing_email = await repo.get_by_email(body.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=body.username,
        email=body.email,
        full_name=body.full_name,
        role=body.role,
        hashed_password=hash_password(body.password),
        department_id=body.department_id,
    )
    await repo.save(user)
    return _to_response(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    repo=Depends(get_user_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _to_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    repo=Depends(get_user_repo),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.full_name is not None:
        user.full_name = body.full_name
    if body.email is not None:
        user.email = body.email
    if body.role is not None:
        user.change_role(body.role)
    if body.department_id is not None:
        user.assign_to_department(body.department_id)
    if body.password is not None:
        user.hashed_password = hash_password(body.password)

    await repo.save(user)
    return _to_response(user)


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    repo=Depends(get_user_repo),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    user.deactivate()
    await repo.save(user)
    return _to_response(user)


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    repo=Depends(get_user_repo),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    await repo.save(user)
    return _to_response(user)
