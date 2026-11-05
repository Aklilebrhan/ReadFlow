import pytest
from httpx import AsyncClient
from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository


@pytest.mark.asyncio
async def test_study_tools(client: AsyncClient, test_db):
    repo = DocumentRepository(test_db)
    doc = Document(
        title="Modern Machine Learning",
        filename="ml.pdf",
        file_type="pdf",
        file_size=1024,
        storage_path="documents/ml.pdf",
        status="Ready",
        raw_text="Supervised learning trains models on labeled datasets to map inputs to target outputs accurately.",
        page_count=1,
        word_count=14
    )
    doc = await repo.create(doc)

    # 1. Flashcards
    fc_res = await client.get(f"/api/v1/study/{doc.id}/flashcards")
    assert fc_res.status_code == 200
    fc_data = fc_res.json()
    assert fc_data["material_type"] == "flashcards"
    assert len(fc_data["items"]) >= 1

    # 2. Quiz
    quiz_res = await client.get(f"/api/v1/study/{doc.id}/quiz")
    assert quiz_res.status_code == 200
    quiz_data = quiz_res.json()
    assert quiz_data["material_type"] == "quiz"
    assert len(quiz_data["items"]) >= 1

    # 3. Key Terms
    terms_res = await client.get(f"/api/v1/study/{doc.id}/key-terms")
    assert terms_res.status_code == 200
    terms_data = terms_res.json()
    assert terms_data["material_type"] == "key_terms"
    assert len(terms_data["items"]) >= 1
