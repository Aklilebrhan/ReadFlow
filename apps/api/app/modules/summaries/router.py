from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.session import get_db
from app.modules.summaries.schemas import SummaryRequest, SummaryResponse
from app.modules.summaries.service import SummaryService

router = APIRouter(prefix="/summaries", tags=["Intelligent Summarization"])


@router.post("", response_model=SummaryResponse)
async def create_document_summary(
    request: SummaryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generates quick, detailed, key points, or hierarchical section-by-section summaries."""
    service = SummaryService(db)
    return await service.generate_document_summary(request)


@router.get("/{document_id}", response_model=SummaryResponse)
async def get_quick_summary(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves or generates a default quick summary for a document."""
    service = SummaryService(db)
    return await service.generate_document_summary(SummaryRequest(document_id=document_id))
