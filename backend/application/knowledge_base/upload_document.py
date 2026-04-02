from typing import Optional
from uuid import UUID

from domain.knowledge_base.entities import DocumentChunk, DocumentType, KnowledgeDocument
from domain.knowledge_base.ports import DocumentParserPort, EmbeddingPort, VectorStorePort
from domain.knowledge_base.repositories import DocumentRepository
from domain.storage.ports import StoragePort
from .chunker import split_text

_EXT_TO_TYPE: dict[str, DocumentType] = {
    ".pdf": DocumentType.PDF,
    ".docx": DocumentType.DOCX,
    ".doc": DocumentType.DOCX,
    ".txt": DocumentType.TXT,
    ".md": DocumentType.TXT,
    ".rst": DocumentType.TXT,
    ".csv": DocumentType.TXT,
}


def _detect_type(filename: str) -> DocumentType:
    for ext, doc_type in _EXT_TO_TYPE.items():
        if filename.lower().endswith(ext):
            return doc_type
    return DocumentType.TXT


class UploadDocumentUseCase:
    def __init__(
        self,
        document_repo: DocumentRepository,
        parsers: list[DocumentParserPort],
        embedder: EmbeddingPort,
        vector_store: VectorStorePort,
        storage: Optional[StoragePort] = None,
        storage_bucket: str = "novadesc-docs",
    ):
        self._repo = document_repo
        self._parsers = parsers
        self._embedder = embedder
        self._vector_store = vector_store
        self._storage = storage
        self._storage_bucket = storage_bucket

    def _find_parser(self, filename: str) -> Optional[DocumentParserPort]:
        return next((p for p in self._parsers if p.supports(filename)), None)

    async def execute(
        self,
        file_bytes: bytes,
        filename: str,
        equipment_id: Optional[UUID] = None,
    ) -> KnowledgeDocument:
        doc = KnowledgeDocument(
            filename=filename,
            doc_type=_detect_type(filename),
            file_size=len(file_bytes),
            equipment_id=equipment_id,
        )
        doc = await self._repo.save(doc)

        try:
            doc.mark_processing()

            if self._storage is not None:
                import mimetypes
                content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
                key = f"knowledge-base/{doc.id}_{filename}"
                await self._storage.upload(self._storage_bucket, key, file_bytes, content_type)
                doc.file_path = key

            await self._repo.save(doc)

            parser = self._find_parser(filename)
            if parser is None:
                raise ValueError(f"Unsupported file type: {filename}")

            raw_text = await parser.parse(file_bytes, filename)
            if not raw_text.strip():
                raise ValueError("Parsed document is empty")

            chunk_texts = split_text(raw_text)
            embeddings = await self._embedder.embed_batch(chunk_texts)

            chunks = [
                DocumentChunk(
                    document_id=doc.id,
                    content=text,
                    chunk_index=idx,
                    embedding=embedding,
                    metadata={"equipment_id": str(equipment_id)} if equipment_id else {},
                )
                for idx, (text, embedding) in enumerate(zip(chunk_texts, embeddings))
            ]

            await self._vector_store.upsert_chunks(chunks)

            doc.mark_ready(chunk_count=len(chunks))
            await self._repo.save(doc)

        except Exception as exc:
            doc.mark_failed(error=str(exc))
            await self._repo.save(doc)
            raise

        return doc
