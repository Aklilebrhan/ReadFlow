import asyncio
import os
import sys
import pymupdf as fitz

# Add apps/api to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api")))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.shared.database.session import init_db
from app.modules.documents.models import Document, Collection
from app.modules.documents.repository import DocumentRepository
from app.modules.ingestion.pipeline import IngestionPipeline
from app.shared.storage import get_storage_service


async def seed():
    print("Seeding sample documents into ReadFlow...")
    await init_db()
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        repo = DocumentRepository(session)
        storage = get_storage_service()

        # 1. Create sample collection
        coll = Collection(
            name="Deep Learning & Document AI",
            description="Foundational papers on Transformer architectures and document intelligence."
        )
        coll = await repo.create_collection(coll)
        print(f"Created collection: '{coll.name}' (ID: {coll.id})")

        # 2. Create synthetic research PDF
        doc = fitz.open()

        # Page 1
        p1 = doc.new_page()
        p1.insert_text((72, 72), "ReadFlow: Modern Architecture for Document Intelligence\n\nAbstract\nThis paper introduces ReadFlow, a modular document intelligence platform that bridges the gap between raw PDF documents and verifiable AI question answering.", fontsize=12)
        p1.insert_text((72, 160), "1. Introduction\nLarge language models require grounded retrieval pipelines to avoid hallucinations. By segmenting documents into semantic passages and indexing them with pgvector, ReadFlow provides page-level citations for every model assertion.", fontsize=11)

        # Page 2
        p2 = doc.new_page()
        p2.insert_text((72, 72), "2. Hybrid Retrieval Methodology\nDense vector embeddings capture conceptual nuances, whereas sparse BM25 indices capture exact proper nouns and numeric figures. ReadFlow employs Reciprocal Rank Fusion (RRF) with alpha=0.6 to combine both rankings into a superior context candidate set.", fontsize=11)
        p2.insert_text((72, 180), "3. Evaluation Benchmarks\nEmpirical benchmarks show an average precision@5 of 0.94 and citation correctness exceeding 98%. When queries fall outside document scope, the system explicitly refuses to hallucinate.", fontsize=11)

        pdf_bytes = doc.tobytes()
        doc.close()

        # Save to storage
        storage_path = "documents/readflow_architecture_paper.pdf"
        await storage.save_file(storage_path, pdf_bytes)

        # Create Document record
        doc_record = Document(
            title="ReadFlow Architecture & Evaluation Paper",
            filename="readflow_architecture_paper.pdf",
            file_type="pdf",
            file_size=len(pdf_bytes),
            storage_path=storage_path,
            status="Uploaded",
            page_count=2,
            collection_id=coll.id
        )
        doc_record = await repo.create(doc_record)
        print(f"Created document record: '{doc_record.title}' (ID: {doc_record.id})")

        # Run ingestion pipeline
        pipeline = IngestionPipeline(session)
        success = await pipeline.process_document(doc_record.id)
        if success:
            print("Successfully processed and indexed document chunks with vector embeddings!")
        else:
            print("Ingestion failed. Check error logs.")

    await engine.dispose()
    print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
