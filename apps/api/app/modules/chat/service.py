from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from app.shared.ai.factory import get_chat_provider
from app.modules.retrieval.service import RetrievalService
from app.modules.chat.schemas import ChatRequest, ChatResponse

logger = get_logger(__name__)


class ChatService:
    """Orchestrates grounded RAG question answering across single or multiple documents."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.retrieval_service = RetrievalService(db)
        self.chat_provider = get_chat_provider()

    async def answer_question(self, req: ChatRequest) -> ChatResponse:
        # 1. Retrieve grounded context chunks
        chunks = await self.retrieval_service.retrieve(
            query=req.query,
            document_id=req.document_id,
            collection_id=req.collection_id,
            document_ids=req.document_ids,
            top_k=req.top_k
        )

        # 2. Format conversation history if supplied
        history_dicts = None
        if req.conversation_history:
            history_dicts = [{"role": m.role, "content": m.content} for m in req.conversation_history]

        # 3. Generate grounded model response
        result = await self.chat_provider.generate_rag_response(
            query=req.query,
            context_chunks=chunks,
            conversation_history=history_dicts
        )

        return ChatResponse(
            answer=result.answer,
            citations=result.citations,
            token_usage=result.token_usage,
            model=result.model,
            provider=result.provider,
            is_mock=result.is_mock
        )
