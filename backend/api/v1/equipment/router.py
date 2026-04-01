from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from application.equipment.commands import (
    CreateEquipmentCommand,
    CreateEquipmentSystemCommand,
    DecommissionEquipmentCommand,
    UpdateEquipmentCommand,
    UpdateEquipmentSystemCommand,
)
from application.equipment.handlers import EquipmentCommandHandler, EquipmentSystemCommandHandler
from core.dependencies import (
    get_current_user,
    get_equipment_repo,
    get_equipment_system_repo,
    require_roles,
)
from domain.equipment.value_objects import EquipmentStatus
from domain.users.entities import User
from domain.users.value_objects import UserRole
from .schemas import (
    EquipmentCreate,
    EquipmentResponse,
    EquipmentSystemCreate,
    EquipmentSystemResponse,
    EquipmentSystemUpdate,
    EquipmentUpdate,
)

router = APIRouter(tags=["equipment"])


def _equipment_response(eq) -> EquipmentResponse:
    mi = None
    if eq.maintenance_interval:
        from .schemas import MaintenanceIntervalSchema
        mi = MaintenanceIntervalSchema(
            value=eq.maintenance_interval.value,
            unit=eq.maintenance_interval.unit,
        )
    return EquipmentResponse(
        id=eq.id,
        name=eq.name,
        serial_number=str(eq.serial_number),
        manufacturer=eq.manufacturer,
        model=eq.model,
        location=eq.location,
        system_id=eq.system_id,
        status=eq.status,
        maintenance_interval=mi,
        installed_at=eq.installed_at,
        metadata=eq.metadata,
        created_at=eq.created_at,
        updated_at=eq.updated_at,
    )


# ── Equipment Systems ─────────────────────────────────────────────────────────

@router.get("/equipment-systems", response_model=List[EquipmentSystemResponse])
async def list_equipment_systems(
    department_id: UUID = Query(...),
    repo=Depends(get_equipment_system_repo),
    _: User = Depends(get_current_user),
):
    items = await repo.list_by_department(department_id)
    return [EquipmentSystemResponse(**s.__dict__) for s in items]


@router.get("/equipment-systems/{system_id}", response_model=EquipmentSystemResponse)
async def get_equipment_system(
    system_id: UUID,
    repo=Depends(get_equipment_system_repo),
    _: User = Depends(get_current_user),
):
    system = await repo.get_by_id(system_id)
    if system is None:
        raise HTTPException(status_code=404, detail="Equipment system not found")
    return EquipmentSystemResponse(**system.__dict__)


@router.post(
    "/equipment-systems",
    response_model=EquipmentSystemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_equipment_system(
    body: EquipmentSystemCreate,
    repo=Depends(get_equipment_system_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    handler = EquipmentSystemCommandHandler(repo)
    try:
        system = await handler.create(CreateEquipmentSystemCommand(**body.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return EquipmentSystemResponse(**system.__dict__)


@router.patch("/equipment-systems/{system_id}", response_model=EquipmentSystemResponse)
async def update_equipment_system(
    system_id: UUID,
    body: EquipmentSystemUpdate,
    repo=Depends(get_equipment_system_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    handler = EquipmentSystemCommandHandler(repo)
    try:
        system = await handler.update(
            UpdateEquipmentSystemCommand(system_id=system_id, **body.model_dump(exclude_none=True))
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return EquipmentSystemResponse(**system.__dict__)


@router.post("/equipment-systems/{system_id}/decommission", response_model=EquipmentSystemResponse)
async def decommission_equipment_system(
    system_id: UUID,
    repo=Depends(get_equipment_system_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    handler = EquipmentSystemCommandHandler(repo)
    try:
        system = await handler.decommission(system_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return EquipmentSystemResponse(**system.__dict__)


# ── Equipment ─────────────────────────────────────────────────────────────────

@router.get("/equipment", response_model=List[EquipmentResponse])
async def list_equipment(
    system_id: Optional[UUID] = Query(None),
    eq_status: Optional[EquipmentStatus] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo=Depends(get_equipment_repo),
    _: User = Depends(get_current_user),
):
    items = await repo.list(system_id=system_id, status=eq_status, limit=limit, offset=offset)
    return [_equipment_response(eq) for eq in items]


@router.get("/equipment/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: UUID,
    repo=Depends(get_equipment_repo),
    _: User = Depends(get_current_user),
):
    eq = await repo.get_by_id(equipment_id)
    if eq is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return _equipment_response(eq)


@router.post("/equipment", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    body: EquipmentCreate,
    repo=Depends(get_equipment_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)),
):
    handler = EquipmentCommandHandler(repo)
    mi = body.maintenance_interval
    try:
        equipment = await handler.create(CreateEquipmentCommand(
            name=body.name,
            serial_number=body.serial_number,
            manufacturer=body.manufacturer,
            model=body.model,
            location=body.location,
            system_id=body.system_id,
            installed_at=body.installed_at,
            interval_value=mi.value if mi else None,
            interval_unit=mi.unit if mi else None,
            metadata=body.metadata,
        ))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _equipment_response(equipment)


@router.patch("/equipment/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: UUID,
    body: EquipmentUpdate,
    repo=Depends(get_equipment_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)),
):
    handler = EquipmentCommandHandler(repo)
    mi = body.maintenance_interval
    try:
        equipment = await handler.update(UpdateEquipmentCommand(
            equipment_id=equipment_id,
            name=body.name,
            location=body.location,
            interval_value=mi.value if mi else None,
            interval_unit=mi.unit if mi else None,
            metadata=body.metadata,
        ))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _equipment_response(equipment)


@router.post("/equipment/{equipment_id}/decommission", response_model=EquipmentResponse)
async def decommission_equipment(
    equipment_id: UUID,
    repo=Depends(get_equipment_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    handler = EquipmentCommandHandler(repo)
    try:
        equipment = await handler.decommission(DecommissionEquipmentCommand(equipment_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _equipment_response(equipment)


@router.post("/equipment/{equipment_id}/set-fault", response_model=EquipmentResponse)
async def set_equipment_fault(
    equipment_id: UUID,
    repo=Depends(get_equipment_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)),
):
    handler = EquipmentCommandHandler(repo)
    try:
        equipment = await handler.set_fault(equipment_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _equipment_response(equipment)


@router.post("/equipment/{equipment_id}/restore", response_model=EquipmentResponse)
async def restore_equipment(
    equipment_id: UUID,
    repo=Depends(get_equipment_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)),
):
    handler = EquipmentCommandHandler(repo)
    try:
        equipment = await handler.restore(equipment_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _equipment_response(equipment)
