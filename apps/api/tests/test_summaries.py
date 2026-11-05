import pytest
from httpx import AsyncClient
from app.modules.documents.models import Document, DocumentChunk
from app.modules.documents.repository import DocumentRepository


@pytest.mark.asyncio
async def test_summaries_and_explanation(client: AsyncClient, test_db):
    repo = DocumentRepository(test_db)
    doc = Document(
        title="Deep Learning Foundations",
        filename="foundations.pdf",
        file_type="pdf",
        file_size=2048,
        storage_path="documents/foundations.pdf",
        status="Ready",
        raw_text="Deep learning enables neural representations to be learned directly from data through backpropagation.",
        page_count=1,
        word_count=14
    )
    doc = await repo.create(doc)

    # 1. Quick Summary
    summary_res = await client.post(
        "/api/v1/summaries",
        json={"document_id": doc.id, "summary_type": "quick"}
    )
    assert summary_res.status_code == 200
    assert "summary" in summary_res.json()
    assert summary_res.json()["document_title"] == "Deep Learning Foundations"

    # 2. Detailed Summary
    detailed_res = await client.post(
        "/api/v1/summaries",
        json={"document_id": doc.id, "summary_type": "detailed"}
    )
    assert detailed_res.status_code == 200
    assert "summary" in detailed_res.json()

    # 3. Passage Explanation
    explain_res = await client.post(
        "/api/v1/explain",
        json={"passage": "Backpropagation computes gradients of the loss function.", "explanation_type": "simple"}
    )
    assert explain_res.status_code == 200
    assert "explanation" in explain_res.json()
