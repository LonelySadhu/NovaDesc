from abc import ABC, abstractmethod
from typing import AsyncIterator


class AIProviderPort(ABC):
    """Port (interface) for AI providers. Adapters: Ollama, Anthropic, OpenAI."""

    @abstractmethod
    async def ask(self, question: str, context: str = "") -> str: ...

    @abstractmethod
    async def ask_stream(self, question: str, context: str = "") -> AsyncIterator[str]: ...

    @abstractmethod
    async def health_check(self) -> bool: ...
