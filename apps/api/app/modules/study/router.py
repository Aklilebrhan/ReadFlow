from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.session import get_db
from app.modules.study.schemas import StudyRequest, StudyResponse, StudyMaterialType
from app.modules.study.service import StudyService

router = APIRouter(prefix="/study", tags=["Study and Research Tools"])


@router.post("/generate", response_model=StudyResponse)
async def generate_study_materials(
    request: StudyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generates study flashcards, multiple-choice quizzes, key terms, or structured notes."""
    service = StudyService(db)
    return await service.generate_materials(request)


@router.get("/{document_id}/flashcards", response_model=StudyResponse)
async def get_document_flashcards(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Generates flashcard deck for document."""
    service = StudyService(db)
    return await service.generate_materials(StudyRequest(document_id=document_id, material_type=StudyMaterialType.FLASHCARDS))


@router.get("/{document_id}/quiz", response_model=StudyResponse)
async def get_document_quiz(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Generates an interactive quiz for document."""
    service = StudyService(db)
    return await service.generate_materials(StudyRequest(document_id=document_id, material_type=StudyMaterialType.QUIZ))


@router.get("/{document_id}/key-terms", response_model=StudyResponse)
async def get_document_key_terms(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Extracts key terms and definitions from document."""
    service = StudyService(db)
    return await service.generate_materials(StudyRequest(document_id=document_id, material_type=StudyMaterialType.KEY_TERMS))
