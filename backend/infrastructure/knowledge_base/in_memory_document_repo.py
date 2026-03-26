from typing import Optional
from uuid import UUID

from domain.knowledge_base.entities import KnowledgeDocument
from domain.knowledge_base.repositories import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    """Temporary in-memory implementation until SQLAlchemy ORM layer is added."""

    def __init__(self) -> None:
        self._store: dict[UUID, KnowledgeDocument] = {}

    async def save(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self._store[document.id] = document
        return document

    async def get_by_id(self, document_id: UUID) -> Optional[KnowledgeDocument]:
        return self._store.get(document_id)

    async def list_all(
        self,
        equipment_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeDocument]:
        items = list(self._store.values())
        if equipment_id is not None:
            items = [d for d in items if d.equipment_id == equipment_id]
        items.sort(key=lambda d: d.created_at, reverse=True)
        return items[offset : offset + limit]

    async def delete(self, document_id: UUID) -> None:
        self._store.pop(document_id, None)
