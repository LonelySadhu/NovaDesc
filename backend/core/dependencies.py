from functools import lru_cache

from core.config import settings, AIProvider, EmbeddingProvider
from domain.ai_assistant.ports import AIProviderPort
from domain.knowledge_base.ports import EmbeddingPort, VectorStorePort


# ── AI provider (LLM) ───────────────────────────────────────────────────────

@lru_cache
def get_ai_provider() -> AIProviderPort:
    if settings.AI_PROVIDER == AIProvider.ANTHROPIC:
        from infrastructure.ai.anthropic_adapter import AnthropicAdapter
        return AnthropicAdapter(
            api_key=settings.ANTHROPIC_API_KEY,
            model=settings.ANTHROPIC_MODEL,
        )
    from infrastructure.ai.ollama_adapter import OllamaAdapter
    return OllamaAdapter(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
    )


# ── Embedder ─────────────────────────────────────────────────────────────────

@lru_cache
def get_embedder() -> EmbeddingPort:
    if settings.EMBEDDING_PROVIDER == EmbeddingProvider.OPENAI:
        from infrastructure.knowledge_base.openai_embedder import OpenAIEmbedder
        return OpenAIEmbedder(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_EMBED_MODEL,
            dim=1536,
        )
    from infrastructure.knowledge_base.ollama_embedder import OllamaEmbedder
    return OllamaEmbedder(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_EMBED_MODEL,
        dim=settings.EMBEDDING_DIM,
    )


# ── Vector store ──────────────────────────────────────────────────────────────

@lru_cache
def get_vector_store() -> VectorStorePort:
    from sqlalchemy.ext.asyncio import create_async_engine
    from infrastructure.knowledge_base.pgvector_store import PgVectorStore

    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    return PgVectorStore(engine=engine, dim=settings.EMBEDDING_DIM)


# ── Document repository (in-memory stub until ORM layer is added) ─────────────

@lru_cache
def get_document_repo():
    from infrastructure.knowledge_base.in_memory_document_repo import InMemoryDocumentRepository
    return InMemoryDocumentRepository()


# ── Knowledge base use cases ─────────────────────────────────────────────────

def get_upload_document_use_case():
    from application.knowledge_base.upload_document import UploadDocumentUseCase
    from infrastructure.knowledge_base.pdf_parser import PDFParser
    from infrastructure.knowledge_base.docx_parser import DOCXParser
    from infrastructure.knowledge_base.text_parser import TextParser

    return UploadDocumentUseCase(
        document_repo=get_document_repo(),
        parsers=[PDFParser(), DOCXParser(), TextParser()],
        embedder=get_embedder(),
        vector_store=get_vector_store(),
    )


def get_search_chunks_use_case():
    from application.knowledge_base.search_chunks import SearchChunksUseCase
    return SearchChunksUseCase(
        embedder=get_embedder(),
        vector_store=get_vector_store(),
    )
