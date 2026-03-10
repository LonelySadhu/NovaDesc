from functools import lru_cache

from core.config import settings, AIProvider
from domain.ai_assistant.ports import AIProviderPort


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
