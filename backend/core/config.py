from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings


class AIProvider(str, Enum):
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"


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

    # AI
    AI_PROVIDER: AIProvider = AIProvider.OLLAMA
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
