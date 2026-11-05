import re
from typing import List, Optional
from app.modules.chunking.base import BaseChunker, RawChunk
from app.modules.extraction.base import ExtractedDocument, ExtractedPage
from app.core.logging import get_logger

logger = get_logger(__name__)


class RecursiveCharacterChunker(BaseChunker):
    """
    Recursive boundary-aware chunker that respects paragraph and sentence breaks,
    preserving page numbers and section headings.
    """

    def chunk_document(
        self,
        extracted: ExtractedDocument,
        chunk_size: int = 800,
        chunk_overlap: int = 150
    ) -> List[RawChunk]:
        chunks: List[RawChunk] = []
        chunk_index = 0
        current_section: Optional[str] = None

        for page in extracted.pages:
            if page.headings:
                current_section = page.headings[0]

            page_text = page.text.strip()
            if not page_text:
                continue

            # Split by double newline (paragraphs) first
            paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]

            current_chunk_text = ""

            for paragraph in paragraphs:
                # If paragraph fits within remaining chunk budget
                if len(current_chunk_text) + len(paragraph) + 2 <= chunk_size:
                    if current_chunk_text:
                        current_chunk_text += "\n\n" + paragraph
                    else:
                        current_chunk_text = paragraph
                else:
                    # Flush accumulated chunk if not empty
                    if current_chunk_text:
                        chunk_index += 1
                        chunks.append(
                            RawChunk(
                                chunk_index=chunk_index,
                                page_number=page.page_number,
                                section_title=current_section,
                                text=current_chunk_text.strip(),
                                word_count=len(current_chunk_text.split())
                            )
                        )
                        # Carry over overlap
                        overlap_text = current_chunk_text[-chunk_overlap:] if len(current_chunk_text) > chunk_overlap else ""
                        current_chunk_text = overlap_text

                    # If the single paragraph itself is larger than chunk_size, split by sentences
                    if len(paragraph) > chunk_size:
                        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                        for s in sentences:
                            s = s.strip()
                            if not s:
                                continue
                            if len(current_chunk_text) + len(s) + 1 <= chunk_size:
                                current_chunk_text += (" " if current_chunk_text else "") + s
                            else:
                                if current_chunk_text:
                                    chunk_index += 1
                                    chunks.append(
                                        RawChunk(
                                            chunk_index=chunk_index,
                                            page_number=page.page_number,
                                            section_title=current_section,
                                            text=current_chunk_text.strip(),
                                            word_count=len(current_chunk_text.split())
                                        )
                                    )
                                    overlap_text = current_chunk_text[-chunk_overlap:] if len(current_chunk_text) > chunk_overlap else ""
                                    current_chunk_text = overlap_text
                                current_chunk_text += (" " if current_chunk_text else "") + s
                    else:
                        current_chunk_text += ("\n\n" if current_chunk_text else "") + paragraph

            # Flush any remaining text at end of page
            if current_chunk_text and len(current_chunk_text.strip()) > 30:
                chunk_index += 1
                chunks.append(
                    RawChunk(
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        section_title=current_section,
                        text=current_chunk_text.strip(),
                        word_count=len(current_chunk_text.split())
                    )
                )

        logger.info(
            "RecursiveCharacterChunker: Generated %d chunks from %d pages (chunk_size=%d, overlap=%d)",
            len(chunks), extracted.page_count, chunk_size, chunk_overlap
        )
        return chunks
