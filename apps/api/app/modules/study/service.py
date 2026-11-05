from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DocumentNotFoundError
from app.modules.documents.repository import DocumentRepository
from app.shared.ai.factory import get_chat_provider
from app.modules.study.schemas import StudyRequest, StudyResponse, StudyMaterialType
from app.core.logging import get_logger

logger = get_logger(__name__)


class StudyService:
    """Generates interactive study materials (flashcards, quizzes, key terms, notes)."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentRepository(db)
        self.chat_provider = get_chat_provider()

    async def generate_materials(self, req: StudyRequest) -> StudyResponse:
        doc = await self.repo.get_by_id(req.document_id)
        if not doc:
            raise DocumentNotFoundError(f"Document {req.document_id} not found.")

        # If page_number is specified, filter chunks by page
        chunks = await self.repo.get_chunks_by_document(doc.id)
        if req.page_number:
            chunks = [c for c in chunks if c.page_number == req.page_number]

        source_text = "\n\n".join(c.text for c in chunks[:10]) if chunks else doc.raw_text or ""

        if req.material_type == StudyMaterialType.NOTES:
            notes = await self.chat_provider.generate_summary(
                source_text,
                summary_type="detailed"
            )
            return StudyResponse(
                document_id=doc.id,
                document_title=doc.title,
                material_type="notes",
                items=[],
                notes_content=notes
            )

        res = await self.chat_provider.generate_study_materials(
            text_content=source_text,
            material_type=req.material_type.value
        )

        items = res.get("items", [])
        return StudyResponse(
            document_id=doc.id,
            document_title=doc.title,
            material_type=req.material_type.value,
            items=items
        )
