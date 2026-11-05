import os
import traceback
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import get_logger
from app.modules.documents.models import Document, DocumentChunk, DocumentStatus
from app.modules.documents.repository import DocumentRepository
from app.modules.extraction.factory import get_extractor_for_file
from app.modules.chunking.factory import get_chunker
from app.modules.embeddings.service import embedding_service
from app.shared.storage import get_storage_service

logger = get_logger(__name__)


class IngestionPipeline:
    """
    End-to-end ingestion pipeline orchestrator.
    Manages extraction, chunking, embedding generation, vector indexing,
    and granular status progression.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentRepository(db)
        self.storage = get_storage_service()

    async def process_document(self, document_id: str) -> bool:
        doc = await self.repo.get_by_id(document_id)
        if not doc:
            logger.error("Ingestion failed: Document %s does not exist.", document_id)
            return False

        logger.info("Starting ingestion pipeline for document '%s' (ID: %s)", doc.title, doc.id)

        try:
            # Stage 1: Retrieve stored file bytes
            await self.repo.update_status(doc.id, DocumentStatus.EXTRACTING, "Reading file bytes from storage...", 15)
            file_bytes = await self.storage.read_file(doc.storage_path)

            # Stage 2: Document Extraction
            await self.repo.update_status(doc.id, DocumentStatus.EXTRACTING, "Extracting text and structural metadata...", 30)
            extractor = get_extractor_for_file(doc.filename)
            extracted = await extractor.extract(file_bytes, doc.filename)

            # Update document stats
            doc.raw_text = extracted.raw_text
            doc.page_count = extracted.page_count
            doc.word_count = extracted.word_count
            doc.extracted_metadata = {
                **extracted.metadata,
                "is_scanned": extracted.is_scanned
            }
            await self.repo.update(doc)

            # Stage 3: Document Chunking
            await self.repo.update_status(doc.id, DocumentStatus.PROCESSING, "Chunking document into semantic passages...", 50)
            chunker = get_chunker(settings.CHUNK_STRATEGY)
            raw_chunks = chunker.chunk_document(
                extracted=extracted,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )

            if not raw_chunks:
                raise ValueError("No valid text chunks could be produced from document content.")

            # Stage 4: Embedding Generation
            await self.repo.update_status(doc.id, DocumentStatus.INDEXING, f"Generating vector embeddings for {len(raw_chunks)} chunks...", 75)
            chunk_texts = [c.text for c in raw_chunks]
            embeddings = await embedding_service.generate_embeddings_for_texts(chunk_texts)

            # Stage 5: Vector Indexing & Persistence
            db_chunks = []
            for raw_chunk, emb in zip(raw_chunks, embeddings):
                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=raw_chunk.chunk_index,
                    page_number=raw_chunk.page_number,
                    section_title=raw_chunk.section_title,
                    text=raw_chunk.text,
                    word_count=raw_chunk.word_count,
                    embedding=emb,
                    chunk_metadata={"section": raw_chunk.section_title}
                )
                db_chunks.append(chunk)

            await self.repo.save_chunks(db_chunks)

            # Stage 6: Completion
            await self.repo.update_status(
                doc.id,
                DocumentStatus.READY,
                f"Successfully indexed {len(db_chunks)} chunks across {doc.page_count} page(s).",
                100
            )
            logger.info("Ingestion completed successfully for document %s (%d chunks)", doc.id, len(db_chunks))
            return True

        except Exception as e:
            error_details = str(e)
            stack = traceback.format_exc()
            logger.error("Ingestion error for document %s: %s\n%s", doc.id, error_details, stack)
            await self.repo.update_status(
                doc.id,
                DocumentStatus.FAILED,
                f"Processing failed: {error_details[:200]}",
                0
            )
            return False
