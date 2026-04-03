import json
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from domain.knowledge_base.entities import DocumentChunk
from domain.knowledge_base.ports import VectorStorePort

# DDL is run once on startup; asyncpg requires separate execute() per statement.
_DDL_STATEMENTS = [
    "CREATE EXTENSION IF NOT EXISTS vector",
    """CREATE TABLE IF NOT EXISTS document_chunks (
    id          UUID        PRIMARY KEY,
    document_id UUID        NOT NULL,
    chunk_index INT         NOT NULL,
    content     TEXT        NOT NULL,
    embedding   vector({dim}),
    metadata    JSONB       NOT NULL DEFAULT '{{}}'
)""",
    """CREATE INDEX IF NOT EXISTS document_chunks_doc_idx
    ON document_chunks (document_id)""",
    """CREATE INDEX IF NOT EXISTS document_chunks_ivfflat_idx
    ON document_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100)""",
]

_UPSERT_SQL = """
INSERT INTO document_chunks (id, document_id, chunk_index, content, embedding, metadata)
VALUES (:id, :document_id, :chunk_index, :content, :embedding, :metadata::jsonb)
ON CONFLICT (id) DO UPDATE
    SET content     = EXCLUDED.content,
        embedding   = EXCLUDED.embedding,
        chunk_index = EXCLUDED.chunk_index,
        metadata    = EXCLUDED.metadata;
"""

_SEARCH_SQL = """
SELECT id, document_id, chunk_index, content, metadata
FROM document_chunks
{where}
ORDER BY embedding <=> :embedding::vector
LIMIT :top_k;
"""

_DELETE_SQL = "DELETE FROM document_chunks WHERE document_id = :document_id;"


class PgVectorStore(VectorStorePort):
    """pgvector-backed vector store using the existing PostgreSQL instance."""

    def __init__(self, engine: AsyncEngine, dim: int = 768):
        self._engine = engine
        self._dim = dim

    async def init(self) -> None:
        """Create extension and table if they don't exist."""
        async with self._engine.begin() as conn:
            for stmt in _DDL_STATEMENTS:
                await conn.execute(text(stmt.format(dim=self._dim)))

    async def upsert_chunks(self, chunks: list[DocumentChunk]) -> None:
        async with self._engine.begin() as conn:
            for chunk in chunks:
                embedding_str = (
                    "[" + ",".join(str(v) for v in chunk.embedding) + "]"
                    if chunk.embedding
                    else None
                )
                await conn.execute(
                    text(_UPSERT_SQL),
                    {
                        "id": str(chunk.id),
                        "document_id": str(chunk.document_id),
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                        "embedding": embedding_str,
                        "metadata": json.dumps(chunk.metadata),
                    },
                )

    async def search(
        self,
        embedding: list[float],
        top_k: int = 5,
        equipment_id: Optional[UUID] = None,
    ) -> list[DocumentChunk]:
        embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"
        params: dict = {"embedding": embedding_str, "top_k": top_k}

        where = ""
        if equipment_id:
            where = (
                "JOIN document_chunks_equipment dce ON dce.chunk_id = id "
                "WHERE dce.equipment_id = :equipment_id"
            )
            params["equipment_id"] = str(equipment_id)

        sql = _SEARCH_SQL.format(where=where)
        async with self._engine.connect() as conn:
            result = await conn.execute(text(sql), params)
            rows = result.fetchall()

        return [
            DocumentChunk(
                id=UUID(row.id) if isinstance(row.id, str) else row.id,
                document_id=UUID(row.document_id) if isinstance(row.document_id, str) else row.document_id,
                chunk_index=row.chunk_index,
                content=row.content,
                metadata=row.metadata if isinstance(row.metadata, dict) else json.loads(row.metadata),
            )
            for row in rows
        ]

    async def delete_by_document(self, document_id: UUID) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(text(_DELETE_SQL), {"document_id": str(document_id)})