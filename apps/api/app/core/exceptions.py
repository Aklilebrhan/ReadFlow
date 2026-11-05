from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class ReadFlowException(Exception):
    """Base exception for all ReadFlow domain and operational errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DocumentNotFoundError(ReadFlowException):
    """Raised when a requested document does not exist."""
    pass


class DocumentProcessingError(ReadFlowException):
    """Raised when document ingestion or processing pipeline fails."""
    pass


class UnsupportedFormatError(ReadFlowException):
    """Raised when an uploaded file format is not supported."""
    pass


class ExtractionError(ReadFlowException):
    """Raised when text or layout extraction fails."""
    pass


class StorageError(ReadFlowException):
    """Raised when file storage or retrieval fails."""
    pass


class RetrievalError(ReadFlowException):
    """Raised when vector or hybrid search fails."""
    pass


class AIProviderError(ReadFlowException):
    """Raised when an external or local AI model provider returns an error."""
    pass


def setup_exception_handlers(app: Any) -> None:
    """Registers standard HTTP exception handlers for domain exceptions."""

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(request, exc: DocumentNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "DocumentNotFound", "message": exc.message, "details": exc.details}
        )

    @app.exception_handler(UnsupportedFormatError)
    async def unsupported_format_handler(request, exc: UnsupportedFormatError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "UnsupportedFormat", "message": exc.message, "details": exc.details}
        )

    @app.exception_handler(DocumentProcessingError)
    async def processing_error_handler(request, exc: DocumentProcessingError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "ProcessingError", "message": exc.message, "details": exc.details}
        )

    @app.exception_handler(AIProviderError)
    async def ai_provider_error_handler(request, exc: AIProviderError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "AIProviderError", "message": exc.message, "details": exc.details}
        )

    @app.exception_handler(ReadFlowException)
    async def general_domain_error_handler(request, exc: ReadFlowException):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalDomainError", "message": exc.message, "details": exc.details}
        )
