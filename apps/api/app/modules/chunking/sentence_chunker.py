import re
from typing import List, Optional
from app.modules.chunking.base import BaseChunker, RawChunk
from app.modules.extraction.base import ExtractedDocument


class SentenceBoundaryChunker(BaseChunker):
    """Chunker that groups complete sentences without ever splitting across a sentence boundary."""

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

            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', page.text) if s.strip()]
            current_sentences: List[str] = []
            current_len = 0

            for sentence in sentences:
                s_len = len(sentence)
                if current_len + s_len <= chunk_size:
                    current_sentences.append(sentence)
                    current_len += s_len + 1
                else:
                    if current_sentences:
                        chunk_index += 1
                        chunk_text = " ".join(current_sentences)
                        chunks.append(
                            RawChunk(
                                chunk_index=chunk_index,
                                page_number=page.page_number,
                                section_title=current_section,
                                text=chunk_text,
                                word_count=len(chunk_text.split())
                            )
                        )
                        # Retain last sentence for overlap if available
                        last_sentence = current_sentences[-1] if len(current_sentences[-1]) < chunk_overlap else ""
                        current_sentences = [last_sentence] if last_sentence else []
                        current_len = len(last_sentence)

                    current_sentences.append(sentence)
                    current_len += s_len + 1

            if current_sentences:
                chunk_index += 1
                chunk_text = " ".join(current_sentences)
                chunks.append(
                    RawChunk(
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        section_title=current_section,
                        text=chunk_text,
                        word_count=len(chunk_text.split())
                    )
                )

        return chunks
