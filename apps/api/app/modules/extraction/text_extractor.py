import re
from typing import List
from app.core.exceptions import ExtractionError
from app.modules.extraction.base import BaseExtractor, ExtractedDocument, ExtractedPage


class TextExtractor(BaseExtractor):
    """Extracts text and markdown headings from .txt and .md files."""

    async def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        # Detect encoding
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                raw_text = file_bytes.decode(encoding).strip()
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ExtractionError("Failed to decode text document with standard encodings.")

        word_count = len(raw_text.split())
        if word_count == 0:
            raise ExtractionError("The text document contains no readable content.")

        # Extract markdown headings (# Heading)
        headings = re.findall(r"^#{1,6}\s+(.+)$", raw_text, flags=re.MULTILINE)

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
            metadata={"filename": filename, "format": "text/markdown"}
        )
