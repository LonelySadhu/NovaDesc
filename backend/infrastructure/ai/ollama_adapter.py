from typing import AsyncIterator

import httpx

from domain.ai_assistant.ports import AIProviderPort


class OllamaAdapter(AIProviderPort):
    """Adapter for local Ollama LLM (no data leaves the network)."""

    def __init__(self, base_url: str, model: str = "llama3"):
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def ask(self, question: str, context: str = "") -> str:
        prompt = self._build_prompt(question, context)
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]

    async def ask_stream(self, question: str, context: str = "") -> AsyncIterator[str]:
        prompt = self._build_prompt(question, context)
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": True},
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if chunk := data.get("response"):
                            yield chunk

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self._base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    def _build_prompt(self, question: str, context: str) -> str:
        if context:
            return (
                f"You are an expert maintenance engineer assistant for high-tech industrial equipment.\n"
                f"Context about the equipment/task:\n{context}\n\n"
                f"Question: {question}"
            )
        return (
            f"You are an expert maintenance engineer assistant for high-tech industrial equipment.\n"
            f"Question: {question}"
        )
