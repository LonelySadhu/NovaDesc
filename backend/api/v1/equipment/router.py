from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from application.equipment.commands import (
    CreateEquipmentCommand,
    UpdateEquipmentCommand,
    DecommissionEquipmentCommand,
)
from application.equipment.handlers import EquipmentCommandHandler
from .schemas import EquipmentCreate, EquipmentUpdate, EquipmentResponse

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("/", response_model=List[EquipmentResponse])
async def list_equipment(
    location: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    # TODO: inject handler via Depends
    pass


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(equipment_id: UUID):
    pass


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(body: EquipmentCreate):
    pass


@router.patch("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(equipment_id: UUID, body: EquipmentUpdate):
    pass


@router.post("/{equipment_id}/decommission", response_model=EquipmentResponse)
async def decommission_equipment(equipment_id: UUID):
    pass
