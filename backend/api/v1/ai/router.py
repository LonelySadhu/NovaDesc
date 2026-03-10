from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["ai"])


class AskRequest(BaseModel):
    question: str
    equipment_id: Optional[UUID] = None
    work_order_id: Optional[UUID] = None


class AskResponse(BaseModel):
    answer: str
    query_id: UUID


@router.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest):
    # TODO: inject AIAssistantService via Depends
    pass


@router.post("/ask/stream")
async def ask_stream(body: AskRequest):
    # TODO: inject AIAssistantService via Depends
    # Returns Server-Sent Events stream
    pass


@router.get("/health")
async def ai_health():
    # TODO: check AI provider availability
    pass
