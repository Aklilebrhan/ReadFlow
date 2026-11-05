from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.session import get_db
from app.modules.chat.schemas import ChatRequest, ChatResponse
from app.modules.chat.service import ChatService

router = APIRouter(prefix="/chat", tags=["AI Document Chat"])


@router.post("", response_model=ChatResponse)
async def chat_with_documents(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a natural language query against a document or multi-document collection.
    Returns a grounded answer with page-level citations.
    """
    service = ChatService(db)
    return await service.answer_question(request)
