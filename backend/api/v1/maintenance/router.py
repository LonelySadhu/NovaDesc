from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_current_user, get_maintenance_schedule_repo, require_roles
from domain.maintenance.entities import MaintenanceSchedule
from domain.maintenance.repositories import MaintenanceScheduleRepository
from domain.users.entities import User
from domain.users.value_objects import UserRole
from .schemas import (
    MaintenanceScheduleCreate,
    MaintenanceScheduleResponse,
    MaintenanceScheduleUpdate,
    RecordCompletion,
)

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


def _schedule_response(s: MaintenanceSchedule) -> MaintenanceScheduleResponse:
    return MaintenanceScheduleResponse(
        id=s.id,
        equipment_id=s.equipment_id,
        title=s.title,
        description=s.description,
        interval_value=s.interval_value,
        interval_unit=s.interval_unit,
        last_performed_at=s.last_performed_at,
        next_due_at=s.next_due_at,
        is_active=s.is_active,
        is_overdue=s.is_overdue,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


@router.get("/", response_model=List[MaintenanceScheduleResponse])
async def list_schedules(
    equipment_id: UUID = Query(...),
    active_only: bool = Query(False),
    repo: MaintenanceScheduleRepository = Depends(get_maintenance_schedule_repo),
    _: User = Depends(get_current_user),
):
    items = await repo.list_by_equipment(equipment_id, active_only=active_only)
    return [_schedule_response(s) for s in items]


@router.get("/overdue", response_model=List[MaintenanceScheduleResponse])
async def list_overdue(
    repo: MaintenanceScheduleRepository = Depends(get_maintenance_schedule_repo),
    _: User = Depends(get_current_user),
):
    items = await repo.list_overdue()
    return [_schedule_response(s) for s in items]


@router.get("/{schedule_id}", response_model=MaintenanceScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    repo: MaintenanceScheduleRepository = Depends(get_maintenance_schedule_repo),
    _: User = Depends(get_current_user),
):
    schedule = await repo.get_by_id(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Maintenance schedule not found")
    return _schedule_response(schedule)


@router.post("/", response_model=MaintenanceScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    body: MaintenanceScheduleCreate,
    repo: MaintenanceScheduleRepository = Depends(get_maintenance_schedule_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)),
):
    try:
        schedule = MaintenanceSchedule(
            equipment_id=body.equipment_id,
            title=body.title,
            description=body.description,
            interval_value=body.interval_value,
            interval_unit=body.interval_unit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    await repo.save(schedule)
    return _schedule_response(schedule)


@router.patch("/{schedule_id}", response_model=MaintenanceScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    body: MaintenanceScheduleUpdate,
    repo: MaintenanceScheduleRepository = Depends(get_maintenance_schedule_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)),
):
    schedule = await repo.get_by_id(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Maintenance schedule not found")
    if body.title is not None:
        schedule.title = body.title
    if body.description is not None:
        schedule.description = body.description
    if body.interval_value is not None:
        schedule.interval_value = body.interval_value
    if body.interval_unit is not None:
        schedule.interval_unit = body.interval_unit
    if body.is_active is not None:
        schedule.is_active = body.is_active
    await repo.save(schedule)
    return _schedule_response(schedule)


@router.post("/{schedule_id}/complete", response_model=MaintenanceScheduleResponse)
async def record_completion(
    schedule_id: UUID,
    body: RecordCompletion,
    repo: MaintenanceScheduleRepository = Depends(get_maintenance_schedule_repo),
    _: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER, UserRole.TECHNICIAN)
    ),
):
    schedule = await repo.get_by_id(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Maintenance schedule not found")
    schedule.record_completion(body.performed_at)
    await repo.save(schedule)
    return _schedule_response(schedule)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: UUID,
    repo: MaintenanceScheduleRepository = Depends(get_maintenance_schedule_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    schedule = await repo.get_by_id(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Maintenance schedule not found")
    await repo.delete(schedule_id)
