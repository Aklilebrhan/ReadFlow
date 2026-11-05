import os
from typing import Optional, List, Tuple
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DocumentNotFoundError, UnsupportedFormatError, DocumentProcessingError
from app.core.logging import get_logger
from app.shared.storage import get_storage_service
from app.modules.documents.models import Document, Collection, DocumentStatus, DocumentHighlight
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import (
    DocumentCreate,
    DocumentUpdate,
    CollectionCreate,
    DocumentContentResponse,
    PageContent,
    DocumentHighlightCreate
)

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".markdown"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class DocumentService:
    """Application service coordinating document lifecycle, storage, and persistence."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentRepository(db)
        self.storage = get_storage_service()

    async def upload_document(
        self,
        file: UploadFile,
        title: Optional[str] = None,
        collection_id: Optional[str] = None
    ) -> Document:
        filename = file.filename or "uploaded_document"
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise UnsupportedFormatError(
                f"File '{filename}' has unsupported extension '{ext}'. Supported formats: PDF, DOCX, TXT, Markdown."
            )

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise DocumentProcessingError(f"File '{filename}' is empty.")
        if file_size > MAX_FILE_SIZE:
            raise DocumentProcessingError(f"File exceeds maximum allowed size of 50MB ({file_size} bytes).")

        # Save to storage
        storage_rel_path = f"documents/{filename}"
        await self.storage.save_file(storage_rel_path, content)

        doc_title = title.strip() if title and title.strip() else os.path.splitext(filename)[0]

        doc = Document(
            title=doc_title,
            filename=filename,
            file_type=ext.lstrip("."),
            file_size=file_size,
            storage_path=storage_rel_path,
            status=DocumentStatus.UPLOADED.value,
            status_message="Uploaded, awaiting extraction pipeline...",
            progress_percent=5,
            collection_id=collection_id
        )

        created_doc = await self.repo.create(doc)
        logger.info("Document registered in database: %s (ID: %s)", created_doc.title, created_doc.id)
        return created_doc

    async def get_document(self, document_id: str) -> Document:
        doc = await self.repo.get_by_id(document_id)
        if not doc:
            raise DocumentNotFoundError(f"Document with ID {document_id} was not found.")
        return doc

    async def list_documents(
        self,
        collection_id: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Document], int]:
        return await self.repo.list_documents(
            collection_id=collection_id,
            search=search,
            status=status,
            skip=skip,
            limit=limit
        )

    async def update_document(self, document_id: str, update_data: DocumentUpdate) -> Document:
        doc = await self.get_document(document_id)
        if update_data.title is not None:
            doc.title = update_data.title
        if update_data.collection_id is not None:
            doc.collection_id = update_data.collection_id
        return await self.repo.update(doc)

    async def delete_document(self, document_id: str) -> bool:
        doc = await self.get_document(document_id)
        # Delete underlying storage
        try:
            await self.storage.delete_file(doc.storage_path)
        except Exception as e:
            logger.warning("Failed to delete underlying storage file: %s", str(e))
        return await self.repo.delete(document_id)

    async def get_document_content(self, document_id: str) -> DocumentContentResponse:
        doc = await self.get_document(document_id)
        chunks = await self.repo.get_chunks_by_document(doc.id)

        # Reconstruct page contents from chunks or raw text
        pages_dict = {}
        for c in chunks:
            p_num = c.page_number
            if p_num not in pages_dict:
                pages_dict[p_num] = {
                    "text_parts": [],
                    "headings": []
                }
            pages_dict[p_num]["text_parts"].append(c.text)
            if c.section_title and c.section_title not in pages_dict[p_num]["headings"]:
                pages_dict[p_num]["headings"].append(c.section_title)

        pages: List[PageContent] = []
        if pages_dict:
            for p_num in sorted(pages_dict.keys()):
                p_text = "\n\n".join(pages_dict[p_num]["text_parts"])
                pages.append(
                    PageContent(
                        page_number=p_num,
                        text=p_text,
                        word_count=len(p_text.split()),
                        headings=pages_dict[p_num]["headings"]
                    )
                )
        else:
            pages.append(
                PageContent(
                    page_number=1,
                    text=doc.raw_text or "Document content is still processing.",
                    word_count=len((doc.raw_text or "").split()),
                    headings=[]
                )
            )

        return DocumentContentResponse(
            id=doc.id,
            title=doc.title,
            file_type=doc.file_type,
            page_count=doc.page_count or len(pages),
            word_count=doc.word_count,
            pages=pages,
            raw_text=doc.raw_text
        )

    # Collections
    async def create_collection(self, data: CollectionCreate) -> Collection:
        coll = Collection(name=data.name, description=data.description)
        return await self.repo.create_collection(coll)

    async def list_collections(self) -> List[dict]:
        pairs = await self.repo.list_collections()
        return [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "document_count": doc_count,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            for c, doc_count in pairs
        ]

    async def delete_collection(self, collection_id: str) -> bool:
        return await self.repo.delete_collection(collection_id)

    # Highlights
    async def add_highlight(self, document_id: str, data: DocumentHighlightCreate) -> DocumentHighlight:
        # Validate doc exists
        await self.get_document(document_id)
        highlight = DocumentHighlight(
            document_id=document_id,
            page_number=data.page_number,
            selected_text=data.selected_text,
            color=data.color,
            note=data.note
        )
        return await self.repo.add_highlight(highlight)

    async def list_highlights(self, document_id: str) -> List[DocumentHighlight]:
        return await self.repo.list_highlights(document_id)

    async def delete_highlight(self, highlight_id: str) -> bool:
        return await self.repo.delete_highlight(highlight_id)
