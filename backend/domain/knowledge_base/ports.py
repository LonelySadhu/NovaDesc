from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .entities import DocumentChunk


class EmbeddingPort(ABC):
    """Port for generating vector embeddings from text."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the embedding vector size."""
        ...


class VectorStorePort(ABC):
    """Port for storing and searching document chunks by semantic similarity."""

    @abstractmethod
    async def upsert_chunks(self, chunks: list[DocumentChunk]) -> None: ...

    @abstractmethod
    async def search(
        self,
        embedding: list[float],
        top_k: int = 5,
        equipment_id: Optional[UUID] = None,
    ) -> list[DocumentChunk]: ...

    @abstractmethod
    async def delete_by_document(self, document_id: UUID) -> None: ...


class DocumentParserPort(ABC):
    """Port for extracting plain text from various file formats."""

    @abstractmethod
    async def parse(self, file_bytes: bytes, filename: str) -> str: ...

    @abstractmethod
    def supports(self, filename: str) -> bool: ...