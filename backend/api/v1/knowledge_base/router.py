from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, status

from application.knowledge_base.search_chunks import SearchChunksUseCase
from application.knowledge_base.upload_document import UploadDocumentUseCase
from core.dependencies import get_upload_document_use_case, get_search_chunks_use_case, get_document_repo
from domain.knowledge_base.repositories import DocumentRepository
from .schemas import ChunkResponse, DocumentListResponse, DocumentResponse

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])

_ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
    "text/markdown",
    "text/csv",
}
_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    equipment_id: Optional[UUID] = Query(None),
    use_case: UploadDocumentUseCase = Depends(get_upload_document_use_case),
):
    """Upload a manual, schema, or any technical document for RAG indexing."""
    file_bytes = await file.read()
    if len(file_bytes) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 50 MB limit")

    background_tasks.add_task(
        use_case.execute,
        file_bytes=file_bytes,
        filename=file.filename or "upload",
        equipment_id=equipment_id,
    )

    # Return a stub response; status will update to READY/FAILED asynchronously
    from domain.knowledge_base.entities import DocumentType, KnowledgeDocument
    from application.knowledge_base.upload_document import _detect_type

    doc = KnowledgeDocument(
        filename=file.filename or "upload",
        doc_type=_detect_type(file.filename or "upload"),
        file_size=len(file_bytes),
        equipment_id=equipment_id,
    )
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        doc_type=doc.doc_type,
        file_size=doc.file_size,
        equipment_id=doc.equipment_id,
        status=doc.status,
        chunk_count=doc.chunk_count,
        error=doc.error,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    equipment_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo: DocumentRepository = Depends(get_document_repo),
):
    items = await repo.list_all(equipment_id=equipment_id, limit=limit, offset=offset)
    return DocumentListResponse(
        items=[DocumentResponse(**d.__dict__) for d in items],
        total=len(items),
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    repo: DocumentRepository = Depends(get_document_repo),
):
    doc = await repo.get_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(**doc.__dict__)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    repo: DocumentRepository = Depends(get_document_repo),
    use_case: SearchChunksUseCase = Depends(get_search_chunks_use_case),
):
    doc = await repo.get_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    # Remove chunks from pgvector first
    from core.dependencies import get_vector_store
    vector_store = get_vector_store()
    await vector_store.delete_by_document(document_id)
    await repo.delete(document_id)


@router.post("/search", response_model=list[ChunkResponse])
async def search_knowledge(
    query: str = Query(..., min_length=3),
    top_k: int = Query(5, ge=1, le=20),
    equipment_id: Optional[UUID] = Query(None),
    use_case: SearchChunksUseCase = Depends(get_search_chunks_use_case),
):
    """Semantic search across indexed documents. Useful for testing RAG retrieval."""
    chunks = await use_case.execute(query=query, top_k=top_k, equipment_id=equipment_id)
    return [
        ChunkResponse(
            id=c.id,
            document_id=c.document_id,
            chunk_index=c.chunk_index,
            content=c.content,
        )
        for c in chunks
    ]
