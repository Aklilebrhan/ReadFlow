from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ExtractedPage(BaseModel):
    """Represents text and structural metadata extracted from a single document page."""
    page_number: int
    text: str
    word_count: int = 0
    headings: List[str] = Field(default_factory=list)


class ExtractedDocument(BaseModel):
    """Normalized document extraction result containing structured pages and document metadata."""
    raw_text: str
    pages: List[ExtractedPage] = Field(default_factory=list)
    page_count: int = 1
    word_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_scanned: bool = False


class BaseExtractor(ABC):
    """Abstract interface for file type content extractors."""

    @abstractmethod
    async def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        """Extracts text, pages, and metadata from raw document bytes."""
        pass
