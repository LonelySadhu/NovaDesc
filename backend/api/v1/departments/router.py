from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_current_user, get_department_repo, require_roles
from domain.departments.entities import Department
from domain.departments.repositories import DepartmentRepository
from domain.users.entities import User
from domain.users.value_objects import UserRole
from .schemas import DepartmentCreate, DepartmentResponse, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("/", response_model=List[DepartmentResponse])
async def list_departments(
    include_inactive: bool = Query(False),
    repo: DepartmentRepository = Depends(get_department_repo),
    _: User = Depends(get_current_user),
):
    items = await repo.list_all(include_inactive=include_inactive)
    return [DepartmentResponse(**d.__dict__) for d in items]


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: UUID,
    repo: DepartmentRepository = Depends(get_department_repo),
    _: User = Depends(get_current_user),
):
    dept = await repo.get_by_id(department_id)
    if dept is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return DepartmentResponse(**dept.__dict__)


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    body: DepartmentCreate,
    repo: DepartmentRepository = Depends(get_department_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    dept = Department(
        name=body.name,
        description=body.description,
        head_id=body.head_id,
        parent_id=body.parent_id,
    )
    await repo.save(dept)
    return DepartmentResponse(**dept.__dict__)


@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: UUID,
    body: DepartmentUpdate,
    repo: DepartmentRepository = Depends(get_department_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    dept = await repo.get_by_id(department_id)
    if dept is None:
        raise HTTPException(status_code=404, detail="Department not found")
    if body.name is not None:
        dept.name = body.name
    if body.description is not None:
        dept.description = body.description
    if body.head_id is not None:
        dept.set_head(body.head_id)
    if body.parent_id is not None:
        dept.parent_id = body.parent_id
    await repo.save(dept)
    return DepartmentResponse(**dept.__dict__)


@router.post("/{department_id}/deactivate", response_model=DepartmentResponse)
async def deactivate_department(
    department_id: UUID,
    repo: DepartmentRepository = Depends(get_department_repo),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    dept = await repo.get_by_id(department_id)
    if dept is None:
        raise HTTPException(status_code=404, detail="Department not found")
    dept.deactivate()
    await repo.save(dept)
    return DepartmentResponse(**dept.__dict__)
