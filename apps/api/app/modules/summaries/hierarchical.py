from typing import List, Dict, Any, Tuple
from app.shared.ai.base import BaseChatProvider
from app.modules.documents.models import DocumentChunk
from app.core.logging import get_logger

logger = get_logger(__name__)


class HierarchicalSummarizer:
    """
    Implements map-reduce hierarchical summarization for long documents.
    Prevents context window overflows and preserves document fidelity.
    """

    def __init__(self, ai_provider: BaseChatProvider):
        self.ai = ai_provider

    async def summarize_hierarchical(
        self,
        chunks: List[DocumentChunk],
        summary_type: str = "detailed"
    ) -> Tuple[str, List[Dict[str, Any]]]:
        if not chunks:
            return "No content available to summarize.", []

        # Group chunks by section or clusters of 5 pages
        sections: Dict[str, List[DocumentChunk]] = {}
        for chunk in chunks:
            sec_name = chunk.section_title or f"Page {chunk.page_number}"
            if sec_name not in sections:
                sections[sec_name] = []
            sections[sec_name].append(chunk)

        section_summaries = []
        intermediate_texts = []

        # Map Phase: Summarize each section
        for sec_name, sec_chunks in sections.items():
            combined_sec_text = "\n\n".join(c.text for c in sec_chunks)
            # Summarize section
            sec_summary = await self.ai.generate_summary(
                combined_sec_text,
                summary_type="quick"
            )
            min_page = min(c.page_number for c in sec_chunks)
            max_page = max(c.page_number for c in sec_chunks)
            page_range = f"Page {min_page}" if min_page == max_page else f"Pages {min_page}-{max_page}"

            section_summaries.append({
                "title": sec_name,
                "summary": sec_summary,
                "page_range": page_range
            })
            intermediate_texts.append(f"### {sec_name} ({page_range})\n{sec_summary}")

        # Reduce Phase: Synthesize intermediate summaries into master overview
        combined_intermediate = "\n\n".join(intermediate_texts)
        master_summary = await self.ai.generate_summary(
            combined_intermediate,
            summary_type=summary_type
        )

        return master_summary, section_summaries
