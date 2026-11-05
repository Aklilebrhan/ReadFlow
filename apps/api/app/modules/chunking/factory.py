from app.core.config import settings
from app.modules.chunking.base import BaseChunker
from app.modules.chunking.recursive_chunker import RecursiveCharacterChunker
from app.modules.chunking.sentence_chunker import SentenceBoundaryChunker


def get_chunker(strategy: str = None) -> BaseChunker:
    """Strategy registry selecting document chunking algorithm."""
    chosen = (strategy or settings.CHUNK_STRATEGY).lower()
    if chosen == "sentence":
        return SentenceBoundaryChunker()
    return RecursiveCharacterChunker()
