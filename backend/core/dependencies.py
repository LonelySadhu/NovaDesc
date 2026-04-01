from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings, AIProvider, EmbeddingProvider
from domain.ai_assistant.ports import AIProviderPort
from domain.knowledge_base.ports import EmbeddingPort, VectorStorePort
from domain.users.entities import User
from domain.users.value_objects import UserRole

_bearer = HTTPBearer()


# ── Database session ──────────────────────────────────────────────────────────

async def get_session() -> AsyncSession:
    from infrastructure.database.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── AI provider (LLM) ────────────────────────────────────────────────────────

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


# ── Embedder ──────────────────────────────────────────────────────────────────

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


# ── Domain repositories ───────────────────────────────────────────────────────

def get_document_repo(session: AsyncSession = Depends(get_session)):
    from infrastructure.repositories.knowledge_base import SqlDocumentRepository
    return SqlDocumentRepository(session)


def get_department_repo(session: AsyncSession = Depends(get_session)):
    from infrastructure.repositories.departments import SqlDepartmentRepository
    return SqlDepartmentRepository(session)


def get_equipment_system_repo(session: AsyncSession = Depends(get_session)):
    from infrastructure.repositories.equipment import SqlEquipmentSystemRepository
    return SqlEquipmentSystemRepository(session)


def get_equipment_repo(session: AsyncSession = Depends(get_session)):
    from infrastructure.repositories.equipment import SqlEquipmentRepository
    return SqlEquipmentRepository(session)


def get_work_order_repo(session: AsyncSession = Depends(get_session)):
    from infrastructure.repositories.work_orders import SqlWorkOrderRepository
    return SqlWorkOrderRepository(session)


def get_spare_part_repo(session: AsyncSession = Depends(get_session)):
    from infrastructure.repositories.spare_parts import SqlSparePartRepository
    return SqlSparePartRepository(session)


def get_purchase_request_repo(session: AsyncSession = Depends(get_session)):
    from infrastructure.repositories.spare_parts import SqlPurchaseRequestRepository
    return SqlPurchaseRequestRepository(session)


def get_maintenance_schedule_repo(session: AsyncSession = Depends(get_session)):
    from infrastructure.repositories.maintenance import SqlMaintenanceScheduleRepository
    return SqlMaintenanceScheduleRepository(session)


# ── Knowledge base use cases ──────────────────────────────────────────────────

def get_upload_document_use_case(
    document_repo=Depends(get_document_repo),
):
    from application.knowledge_base.upload_document import UploadDocumentUseCase
    from infrastructure.knowledge_base.pdf_parser import PDFParser
    from infrastructure.knowledge_base.docx_parser import DOCXParser
    from infrastructure.knowledge_base.text_parser import TextParser

    return UploadDocumentUseCase(
        document_repo=document_repo,
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


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_auth_service(session: AsyncSession = Depends(get_session)):
    from infrastructure.users.repository import SqlUserRepository
    from application.users.service import AuthService
    return AuthService(SqlUserRepository(session))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    from infrastructure.auth.jwt import decode_token
    from infrastructure.users.repository import SqlUserRepository

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    repo = SqlUserRepository(session)
    user = await repo.get_by_id(UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_roles(*roles: UserRole):
    """Dependency factory for RBAC. Usage: Depends(require_roles(UserRole.ADMIN))"""
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return _check
