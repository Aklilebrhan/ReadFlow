import io
from docx import Document as DocxDocument
from typing import List
from app.core.exceptions import ExtractionError
from app.core.logging import get_logger
from app.modules.extraction.base import BaseExtractor, ExtractedDocument, ExtractedPage

logger = get_logger(__name__)


class DocxExtractor(BaseExtractor):
    """Extracts text, paragraphs, and headings from Microsoft Word (.docx) documents."""

    async def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        try:
            doc = DocxDocument(io.BytesIO(file_bytes))
        except Exception as e:
            logger.error("Failed to parse DOCX %s: %s", filename, str(e))
            raise ExtractionError(f"Corrupted or invalid DOCX file: {str(e)}")

        paragraphs = []
        headings = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            if p.style.name.startswith("Heading"):
                headings.append(text)
            paragraphs.append(text)

        # Include table texts
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)

        raw_text = "\n\n".join(paragraphs).strip()
        word_count = len(raw_text.split())

        if word_count == 0:
            raise ExtractionError("The DOCX document is empty.")

        # Simulate pages (~350 words per page standard)
        words = raw_text.split()
        words_per_page = 350
        pages: List[ExtractedPage] = []
        page_num = 1

        for i in range(0, len(words), words_per_page):
            page_text = " ".join(words[i:i + words_per_page])
            pages.append(
                ExtractedPage(
                    page_number=page_num,
                    text=page_text,
                    word_count=len(page_text.split()),
                    headings=[h for h in headings if h in page_text]
                )
            )
            page_num += 1

        return ExtractedDocument(
            raw_text=raw_text,
            pages=pages,
            page_count=len(pages),
            word_count=word_count,
            metadata={"filename": filename, "format": "docx", "heading_count": len(headings)}
        )
