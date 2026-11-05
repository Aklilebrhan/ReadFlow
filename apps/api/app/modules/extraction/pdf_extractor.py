import pymupdf as fitz
from typing import List
from app.core.exceptions import ExtractionError
from app.core.logging import get_logger
from app.modules.extraction.base import BaseExtractor, ExtractedDocument, ExtractedPage
from app.modules.extraction.ocr_engine import ocr_engine

logger = get_logger(__name__)


class PDFExtractor(BaseExtractor):
    """High-performance PDF extractor powered by PyMuPDF (fitz) with OCR fallback."""

    async def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            logger.error("Failed to open PDF %s: %s", filename, str(e))
            raise ExtractionError(f"Corrupted or invalid PDF file: {str(e)}")

        page_count = len(doc)
        if page_count == 0:
            raise ExtractionError("PDF contains 0 pages.")

        pages: List[ExtractedPage] = []
        full_text_parts = []
        is_scanned = False
        scanned_page_count = 0

        for page_index in range(page_count):
            page_num = page_index + 1
            page = doc[page_index]

            # 1. Native text extraction
            text = page.get_text("text").strip()
            headings: List[str] = []

            # 2. Extract structural headings by analyzing font size spans
            try:
                blocks = page.get_text("dict")["blocks"]
                for b in blocks:
                    if "lines" in b:
                        for l in b["lines"]:
                            for s in l["spans"]:
                                # Headings typically have larger font sizes (> 12pt) and short text
                                if s["size"] > 13 and len(s["text"].strip()) > 3 and len(s["text"].strip()) < 80:
                                    headings.append(s["text"].strip())
            except Exception:
                pass

            # 3. Detect scanned/unreadable page (less than 15 characters of text)
            if len(text) < 15:
                scanned_page_count += 1
                logger.info("Page %d of '%s' has minimal text (%d chars). Attempting OCR...", page_num, filename, len(text))
                try:
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    ocr_text = ocr_engine.ocr_image_bytes(img_bytes)
                    if ocr_text:
                        text = ocr_text
                except Exception as ocr_err:
                    logger.warning("OCR failed for page %d: %s", page_num, str(ocr_err))

            word_count = len(text.split())
            pages.append(
                ExtractedPage(
                    page_number=page_num,
                    text=text,
                    word_count=word_count,
                    headings=headings[:5]
                )
            )
            full_text_parts.append(text)

        total_text = "\n\n".join(full_text_parts).strip()
        total_words = sum(p.word_count for p in pages)

        if scanned_page_count > (page_count / 2):
            is_scanned = True

        metadata = {
            "title": doc.metadata.get("title") or filename,
            "author": doc.metadata.get("author") or "",
            "producer": doc.metadata.get("producer") or "",
            "creation_date": doc.metadata.get("creationDate") or "",
            "is_scanned": is_scanned
        }

        doc.close()

        if total_words == 0:
            raise ExtractionError(
                "Document appears empty or contains no readable text. If this is a scanned document, ensure OCR is configured."
            )

        return ExtractedDocument(
            raw_text=total_text,
            pages=pages,
            page_count=page_count,
            word_count=total_words,
            metadata=metadata,
            is_scanned=is_scanned
        )
