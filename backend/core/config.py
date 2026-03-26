from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings


class AIProvider(str, Enum):
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"


class EmbeddingProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "NovaDesc"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://novadesc:novadesc@db:5432/novadesc"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    # AI (LLM)
    AI_PROVIDER: AIProvider = AIProvider.OLLAMA
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # Embeddings (RAG)
    # Ollama uses nomic-embed-text (768-dim, air-gapped).
    # OpenAI uses text-embedding-3-small (1536-dim, requires OPENAI_API_KEY).
    EMBEDDING_PROVIDER: EmbeddingProvider = EmbeddingProvider.OLLAMA
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    EMBEDDING_DIM: int = 768
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"

    # Knowledge base
    RAG_TOP_K: int = 5          # chunks retrieved per query
    RAG_CHUNK_SIZE: int = 800   # characters per chunk
    RAG_CHUNK_OVERLAP: int = 100

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
