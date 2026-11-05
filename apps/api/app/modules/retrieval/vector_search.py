from typing import List, Dict, Any, Optional
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.modules.documents.models import DocumentChunk, Document
from app.core.logging import get_logger

logger = get_logger(__name__)


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorSearchEngine:
    """Performs semantic vector search over document chunks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        query_vector: List[float],
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
        threshold: float = 0.25
    ) -> List[Dict[str, Any]]:
        # Query chunks with their parent document
        stmt = select(DocumentChunk).options(selectinload(DocumentChunk.document))

        if document_ids:
            if len(document_ids) == 1:
                stmt = stmt.where(DocumentChunk.document_id == document_ids[0])
            else:
                stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))

        result = await self.db.execute(stmt)
        chunks = result.scalars().all()

        scored_results = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
            sim = cosine_similarity(query_vector, chunk.embedding)
            if sim >= threshold:
                doc_title = chunk.document.title if chunk.document else "Document"
                scored_results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_title": doc_title,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title,
                    "text": chunk.text,
                    "score": float(sim),
                    "search_type": "vector"
                })

        # Sort by similarity score descending
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]
