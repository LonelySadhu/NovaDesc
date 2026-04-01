from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from application.spare_parts.service import PurchaseRequestService, SparePartService
from core.dependencies import (
    get_current_user,
    get_purchase_request_repo,
    get_spare_part_repo,
    require_roles,
)
from domain.spare_parts.repositories import PurchaseRequestRepository, SparePartRepository
from domain.spare_parts.value_objects import PurchaseRequestStatus
from domain.users.entities import User
from domain.users.value_objects import UserRole
from .schemas import (
    PurchaseRequestCreate,
    PurchaseRequestOrder,
    PurchaseRequestReject,
    PurchaseRequestResponse,
    ReceiveStock,
    ReplaceStock,
    SparePartCreate,
    SparePartMovementResponse,
    SparePartResponse,
    SparePartUpdate,
    WriteOffStock,
)

router = APIRouter(tags=["spare-parts"])


def _part_response(part) -> SparePartResponse:
    return SparePartResponse(
        id=part.id,
        equipment_id=part.equipment_id,
        name=part.name,
        part_number=part.part_number,
        quantity=part.quantity,
        min_stock_level=part.min_stock_level,
        unit=part.unit,
        stock_location=part.stock_location,
        unit_cost=part.unit_cost,
        notes=part.notes,
        status=part.status,
        created_at=part.created_at,
        updated_at=part.updated_at,
    )


# ── Spare Parts ───────────────────────────────────────────────────────────────

@router.get("/spare-parts", response_model=List[SparePartResponse])
async def list_spare_parts(
    equipment_id: UUID = Query(...),
    repo: SparePartRepository = Depends(get_spare_part_repo),
    _: User = Depends(get_current_user),
):
    parts = await repo.list_by_equipment(equipment_id)
    return [_part_response(p) for p in parts]


@router.get("/spare-parts/low-stock", response_model=List[SparePartResponse])
async def list_low_stock(
    repo: SparePartRepository = Depends(get_spare_part_repo),
    _: User = Depends(get_current_user),
):
    parts = await repo.list_low_stock()
    return [_part_response(p) for p in parts]


@router.get("/spare-parts/{spare_part_id}", response_model=SparePartResponse)
async def get_spare_part(
    spare_part_id: UUID,
    repo: SparePartRepository = Depends(get_spare_part_repo),
    _: User = Depends(get_current_user),
):
    part = await repo.get_by_id(spare_part_id)
    if part is None:
        raise HTTPException(status_code=404, detail="Spare part not found")
    return _part_response(part)


@router.post("/spare-parts", response_model=SparePartResponse, status_code=status.HTTP_201_CREATED)
async def create_spare_part(
    body: SparePartCreate,
    repo: SparePartRepository = Depends(get_spare_part_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)),
):
    svc = SparePartService(repo)
    part = await svc.create(
        equipment_id=body.equipment_id,
        name=body.name,
        part_number=body.part_number,
        min_stock_level=body.min_stock_level,
        unit=body.unit,
        stock_location=body.stock_location,
        unit_cost=body.unit_cost,
        notes=body.notes,
    )
    return _part_response(part)


@router.patch("/spare-parts/{spare_part_id}", response_model=SparePartResponse)
async def update_spare_part(
    spare_part_id: UUID,
    body: SparePartUpdate,
    repo: SparePartRepository = Depends(get_spare_part_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)),
):
    part = await repo.get_by_id(spare_part_id)
    if part is None:
        raise HTTPException(status_code=404, detail="Spare part not found")
    if body.name is not None:
        part.name = body.name
    if body.min_stock_level is not None:
        part.min_stock_level = body.min_stock_level
    if body.unit is not None:
        part.unit = body.unit
    if body.stock_location is not None:
        part.stock_location = body.stock_location
    if body.unit_cost is not None:
        part.unit_cost = body.unit_cost
    if body.notes is not None:
        part.notes = body.notes
    await repo.save(part)
    return _part_response(part)


@router.post("/spare-parts/{spare_part_id}/receive", response_model=SparePartMovementResponse)
async def receive_stock(
    spare_part_id: UUID,
    body: ReceiveStock,
    repo: SparePartRepository = Depends(get_spare_part_repo),
    _: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)
    ),
    current_user: User = Depends(get_current_user),
):
    svc = SparePartService(repo)
    try:
        movement = await svc.receive(
            spare_part_id=spare_part_id,
            quantity=body.quantity,
            performed_by=current_user.id,
            unit_cost=body.unit_cost,
            reason=body.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return SparePartMovementResponse(**movement.__dict__)


@router.post("/spare-parts/{spare_part_id}/write-off", response_model=SparePartMovementResponse)
async def write_off_stock(
    spare_part_id: UUID,
    body: WriteOffStock,
    repo: SparePartRepository = Depends(get_spare_part_repo),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)
    ),
):
    svc = SparePartService(repo)
    try:
        movement = await svc.write_off(
            spare_part_id=spare_part_id,
            quantity=body.quantity,
            reason=body.reason,
            performed_by=current_user.id,
            description=body.description,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return SparePartMovementResponse(**movement.__dict__)


@router.post("/spare-parts/{spare_part_id}/replace", response_model=SparePartMovementResponse)
async def replace_stock(
    spare_part_id: UUID,
    body: ReplaceStock,
    repo: SparePartRepository = Depends(get_spare_part_repo),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER, UserRole.TECHNICIAN)
    ),
):
    svc = SparePartService(repo)
    try:
        movement = await svc.replace(
            spare_part_id=spare_part_id,
            quantity=body.quantity,
            work_order_id=body.work_order_id,
            performed_by=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return SparePartMovementResponse(**movement.__dict__)


@router.get("/spare-parts/{spare_part_id}/movements", response_model=List[SparePartMovementResponse])
async def list_movements(
    spare_part_id: UUID,
    repo: SparePartRepository = Depends(get_spare_part_repo),
    _: User = Depends(get_current_user),
):
    part = await repo.get_by_id(spare_part_id)
    if part is None:
        raise HTTPException(status_code=404, detail="Spare part not found")
    return [SparePartMovementResponse(**m.__dict__) for m in part.movements]


# ── Purchase Requests ─────────────────────────────────────────────────────────

@router.get("/purchase-requests", response_model=List[PurchaseRequestResponse])
async def list_purchase_requests(
    pr_status: Optional[PurchaseRequestStatus] = Query(None, alias="status"),
    spare_part_id: Optional[UUID] = Query(None),
    repo: PurchaseRequestRepository = Depends(get_purchase_request_repo),
    _: User = Depends(get_current_user),
):
    if spare_part_id:
        items = await repo.list_by_spare_part(spare_part_id)
    elif pr_status:
        items = await repo.list_by_status(pr_status)
    else:
        items = await repo.list_by_status(PurchaseRequestStatus.DRAFT)
    return [PurchaseRequestResponse(**r.__dict__) for r in items]


@router.get("/purchase-requests/{request_id}", response_model=PurchaseRequestResponse)
async def get_purchase_request(
    request_id: UUID,
    repo: PurchaseRequestRepository = Depends(get_purchase_request_repo),
    _: User = Depends(get_current_user),
):
    req = await repo.get_by_id(request_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Purchase request not found")
    return PurchaseRequestResponse(**req.__dict__)


@router.post("/purchase-requests", response_model=PurchaseRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_request(
    body: PurchaseRequestCreate,
    repo: PurchaseRequestRepository = Depends(get_purchase_request_repo),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)
    ),
):
    svc = PurchaseRequestService(repo)
    req = await svc.create(
        spare_part_id=body.spare_part_id,
        requested_by=current_user.id,
        quantity_needed=body.quantity_needed,
        reason=body.reason,
    )
    return PurchaseRequestResponse(**req.__dict__)


@router.post("/purchase-requests/{request_id}/submit", response_model=PurchaseRequestResponse)
async def submit_purchase_request(
    request_id: UUID,
    repo: PurchaseRequestRepository = Depends(get_purchase_request_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)),
):
    svc = PurchaseRequestService(repo)
    try:
        req = await svc.submit(request_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return PurchaseRequestResponse(**req.__dict__)


@router.post("/purchase-requests/{request_id}/approve", response_model=PurchaseRequestResponse)
async def approve_purchase_request(
    request_id: UUID,
    repo: PurchaseRequestRepository = Depends(get_purchase_request_repo),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    svc = PurchaseRequestService(repo)
    try:
        req = await svc.approve(request_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return PurchaseRequestResponse(**req.__dict__)


@router.post("/purchase-requests/{request_id}/reject", response_model=PurchaseRequestResponse)
async def reject_purchase_request(
    request_id: UUID,
    body: PurchaseRequestReject,
    repo: PurchaseRequestRepository = Depends(get_purchase_request_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    svc = PurchaseRequestService(repo)
    try:
        req = await svc.reject(request_id, body.reason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return PurchaseRequestResponse(**req.__dict__)


@router.post("/purchase-requests/{request_id}/order", response_model=PurchaseRequestResponse)
async def order_purchase_request(
    request_id: UUID,
    body: PurchaseRequestOrder,
    repo: PurchaseRequestRepository = Depends(get_purchase_request_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    svc = PurchaseRequestService(repo)
    try:
        req = await svc.mark_ordered(request_id, body.external_reference)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return PurchaseRequestResponse(**req.__dict__)


@router.post("/purchase-requests/{request_id}/receive", response_model=PurchaseRequestResponse)
async def receive_purchase_request(
    request_id: UUID,
    repo: PurchaseRequestRepository = Depends(get_purchase_request_repo),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    svc = PurchaseRequestService(repo)
    try:
        req = await svc.mark_received(request_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return PurchaseRequestResponse(**req.__dict__)
