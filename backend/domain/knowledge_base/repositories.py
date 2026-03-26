from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .entities import KnowledgeDocument


class DocumentRepository(ABC):
    @abstractmethod
    async def save(self, document: KnowledgeDocument) -> KnowledgeDocument: ...

    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Optional[KnowledgeDocument]: ...

    @abstractmethod
    async def list_all(
        self,
        equipment_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeDocument]: ...

    @abstractmethod
    async def delete(self, document_id: UUID) -> None: ...
