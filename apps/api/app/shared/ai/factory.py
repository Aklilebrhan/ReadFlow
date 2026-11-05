from app.core.config import settings
from app.shared.ai.base import BaseChatProvider, BaseEmbeddingProvider
from app.shared.ai.mock_provider import MockChatProvider, MockEmbeddingProvider
from app.shared.ai.openai_provider import OpenAIChatProvider, OpenAIEmbeddingProvider
from app.shared.ai.gemini_provider import GeminiChatProvider, GeminiEmbeddingProvider
from app.core.logging import get_logger

logger = get_logger(__name__)

_chat_provider_instance: BaseChatProvider = None
_embedding_provider_instance: BaseEmbeddingProvider = None


def get_chat_provider() -> BaseChatProvider:
    """Returns singleton Chat Provider based on AI_PROVIDER environment variable."""
    global _chat_provider_instance
    if _chat_provider_instance is None:
        provider_name = settings.AI_PROVIDER.lower()
        if provider_name == "openai" and settings.OPENAI_API_KEY:
            logger.info("Initializing OpenAI Chat Provider (%s)", settings.OPENAI_CHAT_MODEL)
            _chat_provider_instance = OpenAIChatProvider()
        elif provider_name == "gemini" and settings.GEMINI_API_KEY:
            logger.info("Initializing Google Gemini Chat Provider (%s)", settings.GEMINI_CHAT_MODEL)
            _chat_provider_instance = GeminiChatProvider()
        else:
            logger.info("Initializing Mock AI Chat Provider (Deterministic, Zero-API-Key Mode)")
            _chat_provider_instance = MockChatProvider()
    return _chat_provider_instance


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Returns singleton Embedding Provider based on AI_PROVIDER environment variable."""
    global _embedding_provider_instance
    if _embedding_provider_instance is None:
        provider_name = settings.AI_PROVIDER.lower()
        if provider_name == "openai" and settings.OPENAI_API_KEY:
            logger.info("Initializing OpenAI Embedding Provider (%s)", settings.OPENAI_EMBEDDING_MODEL)
            _embedding_provider_instance = OpenAIEmbeddingProvider()
        elif provider_name == "gemini" and settings.GEMINI_API_KEY:
            logger.info("Initializing Google Gemini Embedding Provider (%s)", settings.GEMINI_EMBEDDING_MODEL)
            _embedding_provider_instance = GeminiEmbeddingProvider()
        else:
            logger.info("Initializing Mock Embedding Provider (384-dimensional vector hashing)")
            _embedding_provider_instance = MockEmbeddingProvider(dimension=384)
    return _embedding_provider_instance
