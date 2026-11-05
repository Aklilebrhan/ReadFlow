import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ReadFlow"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"

    # Server & Networking
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Database: Default to PostgreSQL+asyncpg, but gracefully fallback to sqlite+aiosqlite for testing/dev
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/readflow.db"

    # Storage
    STORAGE_PROVIDER: str = "local"  # "local" or "s3"
    LOCAL_STORAGE_PATH: str = "./data/storage"
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "readflow-documents"
    S3_REGION: str = "us-east-1"

    # AI Configuration
    # Provider options: "mock", "openai", "gemini", "ollama"
    AI_PROVIDER: str = "mock"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_API_BASE: str = "https://api.openai.com/v1"

    # Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_CHAT_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_MODEL: str = "llama3.2"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # Document Chunking
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    CHUNK_STRATEGY: str = "recursive"  # "recursive", "sentence", "section"

    # RAG Retrieval
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_SIMILARITY_THRESHOLD: float = 0.25
    ENABLE_HYBRID_SEARCH: bool = True
    HYBRID_ALPHA: float = 0.6  # 1.0 is vector-only, 0.0 is keyword-only

    # OCR Fallback
    OCR_ENABLED: bool = True
    OCR_ENGINE: str = "tesseract"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
