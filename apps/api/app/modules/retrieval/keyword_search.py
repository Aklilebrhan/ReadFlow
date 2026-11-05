import re
import math
from typing import List, Dict, Any, Optional
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.modules.documents.models import DocumentChunk, Document


class KeywordSearchEngine:
    """Token-based BM25-style keyword search engine for document chunks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
        if not tokens:
            return []

        stmt = select(DocumentChunk).options(selectinload(DocumentChunk.document))
        if document_ids:
            if len(document_ids) == 1:
                stmt = stmt.where(DocumentChunk.document_id == document_ids[0])
            else:
                stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))

        res = await self.db.execute(stmt)
        chunks = res.scalars().all()

        scored_results = []
        q_counter = Counter(tokens)

        for chunk in chunks:
            chunk_tokens = [t.lower() for t in re.findall(r"\w+", chunk.text)]
            if not chunk_tokens:
                continue
            chunk_counter = Counter(chunk_tokens)

            # Simple TF match score
            score = 0.0
            for t, count in q_counter.items():
                if t in chunk_counter:
                    # Term frequency weighted
                    score += (chunk_counter[t] / len(chunk_tokens)) * math.log(1 + count)

            if score > 0:
                doc_title = chunk.document.title if chunk.document else "Document"
                scored_results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_title": doc_title,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title,
                    "text": chunk.text,
                    "score": float(score),
                    "search_type": "keyword"
                })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]
