from typing import Optional, List
from pydantic import BaseModel, Field
from app.shared.ai.base import ChatCitation, TokenUsage


class ChatMessageItem(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = None
    collection_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    conversation_history: Optional[List[ChatMessageItem]] = None
    top_k: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[ChatCitation] = Field(default_factory=list)
    token_usage: TokenUsage
    model: str
    provider: str
    is_mock: bool = False
