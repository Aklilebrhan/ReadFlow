from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.logging import get_logger
from app.modules.documents.models import Document
from app.modules.embeddings.service import embedding_service
from app.modules.retrieval.vector_search import VectorSearchEngine
from app.modules.retrieval.keyword_search import KeywordSearchEngine
from app.modules.retrieval.hybrid_search import reciprocal_rank_fusion

logger = get_logger(__name__)


class RetrievalService:
    """Orchestrates query embedding, multi-document filtering, and hybrid vector+keyword retrieval."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_engine = VectorSearchEngine(db)
        self.keyword_engine = KeywordSearchEngine(db)

    async def retrieve(
        self,
        query: str,
        document_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        k = top_k or settings.RETRIEVAL_TOP_K
        threshold = similarity_threshold or settings.RETRIEVAL_SIMILARITY_THRESHOLD

        target_doc_ids: List[str] = []
        if document_id:
            target_doc_ids.append(document_id)
        elif document_ids:
            target_doc_ids.extend(document_ids)
        elif collection_id:
            # Fetch all documents in collection
            stmt = select(Document.id).where(Document.collection_id == collection_id)
            res = await self.db.execute(stmt)
            target_doc_ids = list(res.scalars().all())

        logger.info(
            "Retrieving context for query: '%s' (filter_docs=%s, top_k=%d)",
            query, target_doc_ids or "all", k
        )

        # 1. Generate query embedding
        query_vector = await embedding_service.generate_query_embedding(query)

        # 2. Perform vector search
        vector_hits = await self.vector_engine.search(
            query_vector=query_vector,
            document_ids=target_doc_ids if target_doc_ids else None,
            top_k=k * 2,
            threshold=threshold
        )

        if not settings.ENABLE_HYBRID_SEARCH:
            return vector_hits[:k]

        # 3. Perform keyword search
        keyword_hits = await self.keyword_engine.search(
            query=query,
            document_ids=target_doc_ids if target_doc_ids else None,
            top_k=k * 2
        )

        # 4. Fuse using Reciprocal Rank Fusion
        fused = reciprocal_rank_fusion(
            vector_results=vector_hits,
            keyword_results=keyword_hits,
            alpha=settings.HYBRID_ALPHA,
            top_k=k
        )

        logger.info("Retrieval returned %d fused candidate chunks", len(fused))
        return fused
