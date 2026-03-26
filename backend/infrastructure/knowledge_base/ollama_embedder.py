import httpx

from domain.knowledge_base.ports import EmbeddingPort


class OllamaEmbedder(EmbeddingPort):
    """Generates embeddings via Ollama (air-gapped, local). Default model: nomic-embed-text."""

    def __init__(self, base_url: str, model: str = "nomic-embed-text", dim: int = 768):
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._dim = dim

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self._base_url}/api/embeddings",
                json={"model": self._model, "prompt": text},
            )
            response.raise_for_status()
            return response.json()["embedding"]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # Ollama doesn't support batch endpoint — run sequentially
        results = []
        for text in texts:
            results.append(await self.embed(text))
        return results