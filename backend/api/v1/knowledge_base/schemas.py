from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from domain.knowledge_base.entities import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    doc_type: DocumentType
    file_size: int
    equipment_id: Optional[UUID]
    status: DocumentStatus
    chunk_count: int
    error: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class ChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
