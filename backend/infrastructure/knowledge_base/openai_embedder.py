from domain.knowledge_base.ports import EmbeddingPort

# Used when AI_PROVIDER=anthropic or EMBEDDING_PROVIDER=openai.
# Anthropic does not expose an embeddings API; OpenAI text-embedding-3-small is
# the recommended cloud alternative (1536-dim).


class OpenAIEmbedder(EmbeddingPort):
    """Generates embeddings via OpenAI (text-embedding-3-small by default)."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small", dim: int = 1536):
        self._api_key = api_key
        self._model = model
        self._dim = dim

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed(self, text: str) -> list[float]:
        results = await self.embed_batch([text])
        return results[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        import httpx

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"input": texts, "model": self._model},
            )
            response.raise_for_status()
            data = response.json()["data"]
            return [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]