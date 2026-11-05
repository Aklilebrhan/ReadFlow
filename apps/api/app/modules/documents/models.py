from datetime import datetime, timezone
import enum
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Text, ForeignKey, Enum, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base, TimestampMixin, generate_uuid
from app.shared.database.vector_type import CompatibleVector


class DocumentStatus(str, enum.Enum):
    UPLOADED = "Uploaded"
    EXTRACTING = "Extracting"
    PROCESSING = "Processing"
    INDEXING = "Indexing"
    READY = "Ready"
    FAILED = "Failed"


class Collection(Base, TimestampMixin):
    __tablename__ = "collections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="collection", lazy="selectin", cascade="all, delete-orphan")


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, docx, txt, md
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)

    # Status tracking
    status: Mapped[str] = mapped_column(String(30), default=DocumentStatus.UPLOADED.value, nullable=False)
    status_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Document stats
    page_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Collection relationship
    collection_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("collections.id", ondelete="SET NULL"), nullable=True)
    collection: Mapped[Optional[Collection]] = relationship("Collection", back_populates="documents", lazy="selectin")

    # Document Chunks
    chunks: Mapped[List["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    highlights: Mapped[List["DocumentHighlight"]] = relationship("DocumentHighlight", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    section_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Vector embedding column (supports 384 dim default)
    embedding: Mapped[Optional[List[float]]] = mapped_column(CompatibleVector(384), nullable=True)
    chunk_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="chunks")


class DocumentHighlight(Base):
    __tablename__ = "document_highlights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    selected_text: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str] = mapped_column(String(30), default="yellow", nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    document: Mapped[Document] = relationship("Document", back_populates="highlights")
