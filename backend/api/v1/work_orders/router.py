from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, status

from application.work_orders.service import WorkOrderService
from core.config import settings
from core.dependencies import get_current_user, get_storage, get_work_order_repo, require_roles
from domain.storage.ports import StoragePort
from domain.users.entities import User
from domain.users.value_objects import UserRole
from domain.work_orders.repositories import WorkOrderRepository
from domain.work_orders.value_objects import WorkOrderPriority, WorkOrderStatus
from .schemas import (
    WorkOrderAssign,
    WorkOrderCancel,
    WorkOrderCreate,
    WorkOrderHold,
    WorkOrderLogCreate,
    WorkOrderLogResponse,
    WorkOrderPhotoResponse,
    WorkOrderResponse,
)

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


def _photo_response(photo, storage: Optional[StoragePort] = None) -> WorkOrderPhotoResponse:
    url = None
    if storage is not None and photo.file_path:
        try:
            url = storage.presigned_url(settings.MINIO_BUCKET_MEDIA, photo.file_path)
        except Exception:
            pass
    return WorkOrderPhotoResponse(**{**photo.__dict__, "url": url})


def _wo_response(order, storage: Optional[StoragePort] = None) -> WorkOrderResponse:
    return WorkOrderResponse(
        id=order.id,
        title=order.title,
        description=order.description,
        equipment_id=order.equipment_id,
        created_by=order.created_by,
        order_type=order.order_type,
        priority=order.priority,
        status=order.status,
        assigned_to=order.assigned_to,
        due_date=order.due_date,
        completed_at=order.completed_at,
        on_hold_reason=order.on_hold_reason,
        cancellation_reason=order.cancellation_reason,
        total_hours=order.total_hours,
        logs=[WorkOrderLogResponse(**log.__dict__) for log in order.logs],
        photos=[_photo_response(p, storage) for p in order.photos],
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.get("/", response_model=List[WorkOrderResponse])
async def list_work_orders(
    equipment_id: Optional[UUID] = Query(None),
    assigned_to: Optional[UUID] = Query(None),
    wo_status: Optional[WorkOrderStatus] = Query(None, alias="status"),
    priority: Optional[WorkOrderPriority] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    storage: StoragePort = Depends(get_storage),
    _: User = Depends(get_current_user),
):
    orders = await repo.list(
        equipment_id=equipment_id,
        assigned_to=assigned_to,
        status=wo_status,
        priority=priority,
        limit=limit,
        offset=offset,
    )
    return [_wo_response(o, storage) for o in orders]


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
async def get_work_order(
    work_order_id: UUID,
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    storage: StoragePort = Depends(get_storage),
    _: User = Depends(get_current_user),
):
    order = await repo.get_by_id(work_order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Work order not found")
    return _wo_response(order, storage)


@router.post("/", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    body: WorkOrderCreate,
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    storage: StoragePort = Depends(get_storage),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.DISPATCHER)
    ),
):
    svc = WorkOrderService(repo)
    try:
        order = await svc.create(
            title=body.title,
            description=body.description,
            equipment_id=body.equipment_id,
            created_by=current_user.id,
            order_type=body.order_type,
            priority=body.priority,
            assigned_to=body.assigned_to,
            due_date=body.due_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _wo_response(order, storage)


@router.post("/{work_order_id}/assign", response_model=WorkOrderResponse)
async def assign_work_order(
    work_order_id: UUID,
    body: WorkOrderAssign,
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    storage: StoragePort = Depends(get_storage),
    _: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.DISPATCHER)
    ),
):
    svc = WorkOrderService(repo)
    try:
        order = await svc.assign(work_order_id, body.technician_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _wo_response(order, storage)


@router.post("/{work_order_id}/hold", response_model=WorkOrderResponse)
async def put_on_hold(
    work_order_id: UUID,
    body: WorkOrderHold,
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    storage: StoragePort = Depends(get_storage),
    _: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER, UserRole.TECHNICIAN)
    ),
):
    svc = WorkOrderService(repo)
    try:
        order = await svc.put_on_hold(work_order_id, body.reason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _wo_response(order, storage)


@router.post("/{work_order_id}/complete", response_model=WorkOrderResponse)
async def complete_work_order(
    work_order_id: UUID,
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    storage: StoragePort = Depends(get_storage),
    _: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER, UserRole.TECHNICIAN)
    ),
):
    svc = WorkOrderService(repo)
    try:
        order = await svc.complete(work_order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _wo_response(order, storage)


@router.post("/{work_order_id}/cancel", response_model=WorkOrderResponse)
async def cancel_work_order(
    work_order_id: UUID,
    body: WorkOrderCancel,
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    storage: StoragePort = Depends(get_storage),
    _: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.DISPATCHER)
    ),
):
    svc = WorkOrderService(repo)
    try:
        order = await svc.cancel(work_order_id, body.reason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _wo_response(order, storage)


@router.post("/{work_order_id}/logs", response_model=WorkOrderLogResponse, status_code=status.HTTP_201_CREATED)
async def add_log(
    work_order_id: UUID,
    body: WorkOrderLogCreate,
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    current_user: User = Depends(get_current_user),
):
    svc = WorkOrderService(repo)
    try:
        log = await svc.add_log(
            work_order_id=work_order_id,
            author_id=current_user.id,
            message=body.message,
            hours_spent=body.hours_spent,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return WorkOrderLogResponse(**log.__dict__)


@router.get("/{work_order_id}/logs", response_model=List[WorkOrderLogResponse])
async def list_logs(
    work_order_id: UUID,
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    _: User = Depends(get_current_user),
):
    logs = await repo.list_logs(work_order_id)
    return [WorkOrderLogResponse(**log.__dict__) for log in logs]


_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_MAX_PHOTO_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/{work_order_id}/photos", response_model=WorkOrderPhotoResponse, status_code=status.HTTP_201_CREATED)
async def add_photo(
    work_order_id: UUID,
    file: UploadFile,
    caption: Optional[str] = Form(None),
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    storage: StoragePort = Depends(get_storage),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER, UserRole.TECHNICIAN)
    ),
):
    file_bytes = await file.read()
    if len(file_bytes) > _MAX_PHOTO_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 20 MB limit")
    if file.content_type not in _ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, WebP, GIF images are allowed")

    photo_id = uuid4()
    original_filename = file.filename or "photo"
    key = f"work-orders/{work_order_id}/{photo_id}_{original_filename}"
    await storage.upload(settings.MINIO_BUCKET_MEDIA, key, file_bytes, file.content_type)

    svc = WorkOrderService(repo)
    try:
        photo = await svc.add_photo(
            work_order_id=work_order_id,
            uploaded_by=current_user.id,
            file_path=key,
            original_filename=original_filename,
            file_size=len(file_bytes),
            caption=caption,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _photo_response(photo, storage)


@router.get("/{work_order_id}/photos", response_model=List[WorkOrderPhotoResponse])
async def list_photos(
    work_order_id: UUID,
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    storage: StoragePort = Depends(get_storage),
    _: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ENGINEER)
    ),
):
    photos = await repo.list_photos(work_order_id)
    return [_photo_response(p, storage) for p in photos]
