from typing import Optional
from uuid import UUID

from domain.knowledge_base.entities import DocumentChunk
from domain.knowledge_base.ports import EmbeddingPort, VectorStorePort


class SearchChunksUseCase:
    def __init__(self, embedder: EmbeddingPort, vector_store: VectorStorePort):
        self._embedder = embedder
        self._vector_store = vector_store

    async def execute(
        self,
        query: str,
        top_k: int = 5,
        equipment_id: Optional[UUID] = None,
    ) -> list[DocumentChunk]:
        embedding = await self._embedder.embed(query)
        return await self._vector_store.search(
            embedding=embedding,
            top_k=top_k,
            equipment_id=equipment_id,
        )

    async def build_context(
        self,
        query: str,
        top_k: int = 5,
        equipment_id: Optional[UUID] = None,
    ) -> str:
        """Returns a formatted string ready for injection into an LLM prompt."""
        chunks = await self.execute(query=query, top_k=top_k, equipment_id=equipment_id)
        if not chunks:
            return ""
        parts = [f"[Document excerpt {i + 1}]\n{chunk.content}" for i, chunk in enumerate(chunks)]
        return "\n\n".join(parts)
