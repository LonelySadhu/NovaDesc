from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    IMAGE = "image"


@dataclass
class KnowledgeDocument:
    filename: str
    doc_type: DocumentType
    file_size: int
    equipment_id: Optional[UUID] = None
    status: DocumentStatus = DocumentStatus.PENDING
    chunk_count: int = 0
    error: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_processing(self) -> None:
        self.status = DocumentStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_ready(self, chunk_count: int) -> None:
        self.status = DocumentStatus.READY
        self.chunk_count = chunk_count
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        self.status = DocumentStatus.FAILED
        self.error = error
        self.updated_at = datetime.utcnow()


@dataclass
class DocumentChunk:
    document_id: UUID
    content: str
    chunk_index: int
    embedding: Optional[list[float]] = None
    metadata: dict = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
