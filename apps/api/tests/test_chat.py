import pytest
from httpx import AsyncClient
from app.modules.documents.models import Document, DocumentChunk
from app.modules.documents.repository import DocumentRepository
from app.shared.ai.factory import get_embedding_provider


@pytest.mark.asyncio
async def test_chat_grounding_and_citations(client: AsyncClient, test_db):
    repo = DocumentRepository(test_db)
    emb_provider = get_embedding_provider()

    # Create test document
    doc = Document(
        title="Attention Mechanism Guide",
        filename="attention.pdf",
        file_type="pdf",
        file_size=1024,
        storage_path="documents/attention.pdf",
        status="Ready",
        page_count=2,
        word_count=50
    )
    doc = await repo.create(doc)

    # Create indexed chunks
    chunk_text = "Transformers replace recurrent neural networks with multi-head self-attention mechanisms."
    emb = await emb_provider.embed_query(chunk_text)

    chunk = DocumentChunk(
        document_id=doc.id,
        chunk_index=1,
        page_number=1,
        section_title="Introduction",
        text=chunk_text,
        word_count=10,
        embedding=emb
    )
    await repo.save_chunks([chunk])

    # Ask grounded question
    chat_payload = {
        "query": "What do transformers replace?",
        "document_id": doc.id
    }
    chat_res = await client.post("/api/v1/chat", json=chat_payload)
    assert chat_res.status_code == 200
    res_data = chat_res.json()

    assert "answer" in res_data
    assert len(res_data["citations"]) >= 1
    assert res_data["citations"][0]["page_number"] == 1
    assert res_data["citations"][0]["document_title"] == "Attention Mechanism Guide"
    assert "token_usage" in res_data


@pytest.mark.asyncio
async def test_chat_unsupported_question_refusal(client: AsyncClient, test_db):
    # Query with non-existent document
    chat_payload = {
        "query": "What happened in the year 3050 on Neptune?",
        "document_id": "non-existent-id"
    }
    chat_res = await client.post("/api/v1/chat", json=chat_payload)
    assert chat_res.status_code == 200
    res_data = chat_res.json()

    # Verify that model admits answer is not found
    assert "could not find information" in res_data["answer"].lower()
    assert len(res_data["citations"]) == 0
