from typing import List
from app.shared.ai.factory import get_embedding_provider
from app.shared.ai.base import BaseEmbeddingProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service orchestrating batch embedding generation and dimension checks."""

    def __init__(self, provider: BaseEmbeddingProvider = None):
        self.provider = provider or get_embedding_provider()

    @property
    def dimension(self) -> int:
        return self.provider.dimension

    async def generate_embeddings_for_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = await self.provider.embed_texts(batch)
            all_embeddings.extend(embeddings)
        return all_embeddings

    async def generate_query_embedding(self, query: str) -> List[float]:
        return await self.provider.embed_query(query)


embedding_service = EmbeddingService()
