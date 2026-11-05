import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api")))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.modules.documents.repository import DocumentRepository
from app.modules.chat.service import ChatService
from app.modules.chat.schemas import ChatRequest
from app.modules.summaries.service import SummaryService
from app.modules.summaries.schemas import SummaryRequest, SummaryType
from app.modules.explanation.service import explanation_service
from app.modules.explanation.schemas import ExplainRequest, ExplanationType
from app.modules.study.service import StudyService
from app.modules.study.schemas import StudyRequest, StudyMaterialType


async def verify_system():
    print("==================================================")
    print(" Running End-to-End ReadFlow System Verification")
    print("==================================================")
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        repo = DocumentRepository(session)
        docs, count = await repo.list_documents()
        print(f"1. Documents in library: {count}")
        assert count > 0, "No documents found in library"
        doc = docs[0]
        print(f"   Selected Doc: '{doc.title}' (Status: {doc.status}, Pages: {doc.page_count})")

        # 2. Test Grounded RAG Chat
        print("\n2. Testing Grounded RAG Chat...")
        chat_service = ChatService(session)
        chat_req = ChatRequest(
            query="What retrieval methodology does ReadFlow employ?",
            document_id=doc.id
        )
        chat_res = await chat_service.answer_question(chat_req)
        print(f"   AI Answer:\n   {chat_res.answer[:200]}...")
        print(f"   Citations Returned: {len(chat_res.citations)}")
        for c in chat_res.citations:
            print(f"   - Citation [{c.citation_id}]: Page {c.page_number} ('{c.snippet[:60]}...')")
        assert len(chat_res.citations) > 0, "Expected at least one citation"

        # 3. Test Grounded Refusal
        print("\n3. Testing Grounded Refusal for Out-of-Scope Query...")
        refusal_req = ChatRequest(
            query="What is the speed of light in deep water?",
            document_id=doc.id
        )
        refusal_res = await chat_service.answer_question(refusal_req)
        print(f"   Refusal Answer:\n   {refusal_res.answer}")
        assert "could not find information" in refusal_res.answer.lower()

        # 4. Test Summaries
        print("\n4. Testing Summarization...")
        summary_service = SummaryService(session)
        summary_res = await summary_service.generate_document_summary(
            SummaryRequest(document_id=doc.id, summary_type=SummaryType.KEY_POINTS)
        )
        print(f"   Key Points Summary:\n   {summary_res.summary[:200]}...")

        # 5. Test Explanation
        print("\n5. Testing Passage Explanation...")
        explain_res = await explanation_service.explain(
            ExplainRequest(
                passage="ReadFlow employs Reciprocal Rank Fusion (RRF) with alpha=0.6.",
                explanation_type=ExplanationType.SIMPLE
            )
        )
        print(f"   Explanation:\n   {explain_res.explanation[:200]}...")

        # 6. Test Study Tools
        print("\n6. Testing Study Materials Generation...")
        study_service = StudyService(session)
        flashcards_res = await study_service.generate_materials(
            StudyRequest(document_id=doc.id, material_type=StudyMaterialType.FLASHCARDS)
        )
        print(f"   Flashcards Generated: {len(flashcards_res.items)}")
        for idx, fc in enumerate(flashcards_res.items[:2], 1):
            print(f"   - Card {idx}: Q: {fc.get('front')} | A: {fc.get('back')[:50]}...")

    await engine.dispose()
    print("\n==================================================")
    print(" ALL END-TO-END VERIFICATION CHECKS PASSED (100%)")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(verify_system())
