from typing import AsyncIterator

import anthropic

from domain.ai_assistant.ports import AIProviderPort


class AnthropicAdapter(AIProviderPort):
    """Adapter for Anthropic Claude API (cloud option, requires API key)."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def ask(self, question: str, context: str = "") -> str:
        messages = [{"role": "user", "content": self._build_message(question, context)}]
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=2048,
            system=(
                "You are an expert maintenance engineer assistant for high-tech industrial equipment "
                "such as data centers, vessels, and industrial facilities. "
                "Provide precise, actionable technical guidance."
            ),
            messages=messages,
        )
        return response.content[0].text

    async def ask_stream(self, question: str, context: str = "") -> AsyncIterator[str]:
        messages = [{"role": "user", "content": self._build_message(question, context)}]
        async with self._client.messages.stream(
            model=self._model,
            max_tokens=2048,
            system=(
                "You are an expert maintenance engineer assistant for high-tech industrial equipment."
            ),
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def health_check(self) -> bool:
        try:
            await self._client.messages.create(
                model=self._model,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception:
            return False

    def _build_message(self, question: str, context: str) -> str:
        if context:
            return f"Context:\n{context}\n\nQuestion: {question}"
        return question
