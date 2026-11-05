from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from sqlalchemy.orm import selectinload
from app.modules.documents.models import Document, Collection, DocumentChunk, DocumentHighlight, DocumentStatus


class DocumentRepository:
    """Async repository for Document and Collection persistence."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, document_id: str) -> Optional[Document]:
        stmt = (
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.collection))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_documents(
        self,
        collection_id: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Document], int]:
        stmt = select(Document).options(selectinload(Document.collection))

        if collection_id:
            stmt = stmt.where(Document.collection_id == collection_id)
        if search:
            stmt = stmt.where(
                or_(
                    Document.title.ilike(f"%{search}%"),
                    Document.filename.ilike(f"%{search}%")
                )
            )
        if status:
            stmt = stmt.where(Document.status == status)

        # Count total
        count_stmt = select(func.count(Document.id)).select_from(Document)
        if collection_id:
            count_stmt = count_stmt.where(Document.collection_id == collection_id)
        if search:
            count_stmt = count_stmt.where(
                or_(Document.title.ilike(f"%{search}%"), Document.filename.ilike(f"%{search}%"))
            )
        if status:
            count_stmt = count_stmt.where(Document.status == status)

        total_res = await self.db.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = stmt.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all()), total

    async def create(self, document: Document) -> Document:
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def update(self, document: Document) -> Document:
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        message: Optional[str] = None,
        progress: Optional[int] = None
    ) -> None:
        doc = await self.get_by_id(document_id)
        if doc:
            doc.status = status.value
            if message is not None:
                doc.status_message = message
            if progress is not None:
                doc.progress_percent = progress
            await self.db.commit()

    async def delete(self, document_id: str) -> bool:
        stmt = delete(Document).where(Document.id == document_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    async def save_chunks(self, chunks: List[DocumentChunk]) -> None:
        self.db.add_all(chunks)
        await self.db.commit()

    async def get_chunks_by_document(self, document_id: str) -> List[DocumentChunk]:
        stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Collections
    async def create_collection(self, collection: Collection) -> Collection:
        self.db.add(collection)
        await self.db.commit()
        await self.db.refresh(collection)
        return collection

    async def get_collection_by_id(self, collection_id: str) -> Optional[Collection]:
        stmt = select(Collection).where(Collection.id == collection_id).options(selectinload(Collection.documents))
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_collections(self) -> List[Tuple[Collection, int]]:
        stmt = (
            select(Collection, func.count(Document.id))
            .outerjoin(Document, Document.collection_id == Collection.id)
            .group_by(Collection.id)
            .order_by(Collection.name.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.all())

    async def delete_collection(self, collection_id: str) -> bool:
        stmt = delete(Collection).where(Collection.id == collection_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    # Highlights
    async def add_highlight(self, highlight: DocumentHighlight) -> DocumentHighlight:
        self.db.add(highlight)
        await self.db.commit()
        await self.db.refresh(highlight)
        return highlight

    async def list_highlights(self, document_id: str) -> List[DocumentHighlight]:
        stmt = select(DocumentHighlight).where(DocumentHighlight.document_id == document_id).order_by(DocumentHighlight.page_number, DocumentHighlight.created_at)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def delete_highlight(self, highlight_id: str) -> bool:
        stmt = delete(DocumentHighlight).where(DocumentHighlight.id == highlight_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0
