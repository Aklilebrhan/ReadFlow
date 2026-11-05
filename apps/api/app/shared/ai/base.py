from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatCitation(BaseModel):
    """Citation referencing a specific chunk and document page."""
    citation_id: int
    document_id: str
    document_title: str
    page_number: Optional[int] = None
    chunk_id: str
    snippet: str
    relevance_score: Optional[float] = None


class TokenUsage(BaseModel):
    """Token consumption and financial cost metrics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class ChatCompletionResult(BaseModel):
    """Result returned by LLM chat generation."""
    answer: str
    citations: List[ChatCitation] = Field(default_factory=list)
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    model: str
    provider: str
    is_mock: bool = False


class BaseEmbeddingProvider(ABC):
    """Abstract interface for text embedding generation."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the dimensionality of generated vector embeddings."""
        pass

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text chunks."""
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """Generates embedding for a single user query."""
        pass


class BaseChatProvider(ABC):
    """Abstract interface for LLM chat and text generation."""

    @abstractmethod
    async def generate_rag_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None
    ) -> ChatCompletionResult:
        """Generates a grounded answer citing the retrieved context chunks."""
        pass

    @abstractmethod
    async def generate_summary(
        self,
        text_content: str,
        summary_type: str = "quick",
        instructions: Optional[str] = None
    ) -> str:
        """Generates a summary of the provided text."""
        pass

    @abstractmethod
    async def explain_passage(
        self,
        passage: str,
        explanation_type: str = "simple"
    ) -> str:
        """Explains a passage simply, technically, or defines terms."""
        pass

    @abstractmethod
    async def generate_study_materials(
        self,
        text_content: str,
        material_type: str = "flashcards"
    ) -> Dict[str, Any]:
        """Generates flashcards, quiz questions, or key terms from document text."""
        pass
