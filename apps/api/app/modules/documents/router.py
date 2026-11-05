from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.session import get_db, async_session_factory
from app.modules.documents.schemas import (
    DocumentResponse,
    DocumentStatusResponse,
    DocumentUpdate,
    CollectionCreate,
    CollectionResponse,
    DocumentChunkResponse,
    DocumentContentResponse,
    DocumentHighlightCreate,
    DocumentHighlightResponse
)
from app.modules.documents.service import DocumentService
from app.modules.ingestion.pipeline import IngestionPipeline
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Documents & Collections"])


async def run_ingestion_background(document_id: str):
    """Background task running the full ingestion pipeline in its own database session."""
    async with async_session_factory() as session:
        try:
            pipeline = IngestionPipeline(session)
            await pipeline.process_document(document_id)
        except Exception as e:
            logger.error("Background ingestion failed for %s: %s", document_id, str(e))


# ---------------------------------------------------------
# Document Lifecycle & Status
# ---------------------------------------------------------

@router.post("/documents/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    collection_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Uploads a document (PDF, DOCX, TXT, MD), validates size/type,
    stores the raw file, and queues the asynchronous ingestion pipeline.
    """
    service = DocumentService(db)
    doc = await service.upload_document(file=file, title=title, collection_id=collection_id)

    # Trigger async background ingestion
    background_tasks.add_task(run_ingestion_background, doc.id)
    return doc


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    collection_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves list of documents with optional filtering by title or collection."""
    service = DocumentService(db)
    docs, _ = await service.list_documents(
        collection_id=collection_id,
        search=search,
        status=status,
        skip=skip,
        limit=limit
    )
    return docs


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves document metadata by ID."""
    service = DocumentService(db)
    return await service.get_document(document_id)


@router.patch("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Updates document title or collection assignment."""
    service = DocumentService(db)
    return await service.update_document(document_id, update_data)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deletes a document, its chunks, highlights, and underlying storage file."""
    service = DocumentService(db)
    await service.delete_document(document_id)
    return None


@router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Polls real-time document processing progress and status messages."""
    service = DocumentService(db)
    doc = await service.get_document(document_id)
    return DocumentStatusResponse(
        id=doc.id,
        status=doc.status,
        status_message=doc.status_message,
        progress_percent=doc.progress_percent
    )


@router.get("/documents/{document_id}/content", response_model=DocumentContentResponse)
async def get_document_content(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves structured page contents and raw text for the reader interface."""
    service = DocumentService(db)
    return await service.get_document_content(document_id)


@router.get("/documents/{document_id}/chunks", response_model=List[DocumentChunkResponse])
async def get_document_chunks(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Lists indexed semantic chunks for a document."""
    service = DocumentService(db)
    chunks = await service.repo.get_chunks_by_document(document_id)
    return chunks


# ---------------------------------------------------------
# Document Highlights (Reader Tool)
# ---------------------------------------------------------

@router.post("/documents/{document_id}/highlights", response_model=DocumentHighlightResponse, status_code=status.HTTP_201_CREATED)
async def add_document_highlight(
    document_id: str,
    data: DocumentHighlightCreate,
    db: AsyncSession = Depends(get_db)
):
    """Saves a highlighted text passage with color and optional notes."""
    service = DocumentService(db)
    return await service.add_highlight(document_id, data)


@router.get("/documents/{document_id}/highlights", response_model=List[DocumentHighlightResponse])
async def list_document_highlights(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Lists all saved highlights for a document."""
    service = DocumentService(db)
    return await service.list_highlights(document_id)


@router.delete("/documents/highlights/{highlight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_highlight(
    highlight_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deletes a saved highlight."""
    service = DocumentService(db)
    await service.delete_highlight(highlight_id)
    return None


# ---------------------------------------------------------
# Collections
# ---------------------------------------------------------

@router.post("/collections", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    data: CollectionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Creates a new document collection."""
    service = DocumentService(db)
    return await service.create_collection(data)


@router.get("/collections", response_model=List[CollectionResponse])
async def list_collections(
    db: AsyncSession = Depends(get_db)
):
    """Lists all collections with their associated document count."""
    service = DocumentService(db)
    return await service.list_collections()


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deletes a collection."""
    service = DocumentService(db)
    await service.delete_collection(collection_id)
    return None
