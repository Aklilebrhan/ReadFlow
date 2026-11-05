from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DocumentNotFoundError
from app.modules.documents.repository import DocumentRepository
from app.shared.ai.factory import get_chat_provider
from app.modules.summaries.schemas import SummaryRequest, SummaryResponse, SectionSummary
from app.modules.summaries.hierarchical import HierarchicalSummarizer
from app.core.logging import get_logger

logger = get_logger(__name__)


class SummaryService:
    """Service handling multi-level document summarization."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentRepository(db)
        self.chat_provider = get_chat_provider()
        self.hierarchical_summarizer = HierarchicalSummarizer(self.chat_provider)

    async def generate_document_summary(self, req: SummaryRequest) -> SummaryResponse:
        doc = await self.repo.get_by_id(req.document_id)
        if not doc:
            raise DocumentNotFoundError(f"Document {req.document_id} not found.")

        chunks = await self.repo.get_chunks_by_document(doc.id)

        # If document has more than 8 chunks (~3,000 words), perform hierarchical summarization
        is_hierarchical = len(chunks) > 8

        if is_hierarchical:
            logger.info("Executing hierarchical map-reduce summarization for document %s (%d chunks)", doc.id, len(chunks))
            master_summary, raw_sections = await self.hierarchical_summarizer.summarize_hierarchical(
                chunks=chunks,
                summary_type=req.summary_type.value
            )
            sections = [
                SectionSummary(
                    title=s["title"],
                    summary=s["summary"],
                    page_range=s.get("page_range")
                )
                for s in raw_sections
            ]
        else:
            text_to_summarize = doc.raw_text or "\n\n".join(c.text for c in chunks)
            master_summary = await self.chat_provider.generate_summary(
                text_content=text_to_summarize,
                summary_type=req.summary_type.value,
                instructions=req.custom_instructions
            )
            sections = []

        return SummaryResponse(
            document_id=doc.id,
            document_title=doc.title,
            summary_type=req.summary_type.value,
            summary=master_summary,
            sections=sections,
            word_count=len(master_summary.split()),
            is_hierarchical=is_hierarchical
        )
