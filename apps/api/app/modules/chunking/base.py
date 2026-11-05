from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field
from app.modules.extraction.base import ExtractedDocument


class RawChunk(BaseModel):
    """Normalized chunk metadata and content."""
    chunk_index: int
    page_number: int
    section_title: Optional[str] = None
    text: str
    word_count: int = 0


class BaseChunker(ABC):
    """Abstract interface for replaceable document chunking strategies."""

    @abstractmethod
    def chunk_document(
        self,
        extracted: ExtractedDocument,
        chunk_size: int = 800,
        chunk_overlap: int = 150
    ) -> List[RawChunk]:
        """Splits an extracted document into structured semantic chunks preserving page and section context."""
        pass
