from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.knowledge_base.entities import DocumentStatus, DocumentType, KnowledgeDocument
from domain.knowledge_base.repositories import DocumentRepository
from infrastructure.database.models.knowledge_base import KnowledgeDocumentModel


class SqlDocumentRepository(DocumentRepository):
    """
    SQL-реализация DocumentRepository.

    Примечание: KnowledgeDocumentModel требует file_path (путь в MinIO), но
    доменная сущность KnowledgeDocument этого поля не имеет — MinIO-интеграция
    добавляется отдельно. До её реализации file_path хранится как пустая строка.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, document: KnowledgeDocument) -> KnowledgeDocument:
        row = await self._session.get(KnowledgeDocumentModel, document.id)
        if row is None:
            row = KnowledgeDocumentModel(
                id=document.id,
                filename=document.filename,
                doc_type=document.doc_type.value,
                file_size=document.file_size,
                equipment_id=document.equipment_id,
                status=document.status.value,
                chunk_count=document.chunk_count,
                file_path="",
                created_at=document.created_at,
            )
            self._session.add(row)
        else:
            row.filename = document.filename
            row.doc_type = document.doc_type.value
            row.file_size = document.file_size
            row.equipment_id = document.equipment_id
            row.status = document.status.value
            row.chunk_count = document.chunk_count
        await self._session.flush()
        return document

    async def get_by_id(self, document_id: UUID) -> Optional[KnowledgeDocument]:
        row = await self._session.get(KnowledgeDocumentModel, document_id)
        return self._to_entity(row) if row else None

    async def list_all(
        self,
        equipment_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[KnowledgeDocument]:
        stmt = select(KnowledgeDocumentModel).order_by(
            KnowledgeDocumentModel.created_at.desc()
        )
        if equipment_id is not None:
            stmt = stmt.where(KnowledgeDocumentModel.equipment_id == equipment_id)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars()]

    async def delete(self, document_id: UUID) -> None:
        row = await self._session.get(KnowledgeDocumentModel, document_id)
        if row:
            await self._session.delete(row)
            await self._session.flush()

    @staticmethod
    def _to_entity(row: KnowledgeDocumentModel) -> KnowledgeDocument:
        return KnowledgeDocument(
            id=row.id,
            filename=row.filename,
            doc_type=DocumentType(row.doc_type),
            file_size=row.file_size,
            equipment_id=row.equipment_id,
            status=DocumentStatus(row.status),
            chunk_count=row.chunk_count,
            created_at=row.created_at,
        )
