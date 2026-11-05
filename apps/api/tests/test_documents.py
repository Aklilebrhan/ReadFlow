import pytest
from httpx import AsyncClient
import pymupdf as fitz


@pytest.mark.asyncio
async def test_document_lifecycle(client: AsyncClient):
    # 1. Create collection
    col_res = await client.post("/api/v1/collections", json={"name": "AI Papers", "description": "Machine learning literature"})
    assert col_res.status_code == 201
    collection_id = col_res.json()["id"]

    # 2. Upload document
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Document Intelligence Research\n\nDeep learning models transform document processing.")
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("research_paper.pdf", pdf_bytes, "application/pdf")}
    data = {"title": "Doc Intelligence", "collection_id": collection_id}

    upload_res = await client.post("/api/v1/documents/upload", files=files, data=data)
    assert upload_res.status_code == 201
    doc_data = upload_res.json()
    doc_id = doc_data["id"]
    assert doc_data["title"] == "Doc Intelligence"

    # 3. Check status
    status_res = await client.get(f"/api/v1/documents/{doc_id}/status")
    assert status_res.status_code == 200
    assert "status" in status_res.json()

    # 4. List documents
    list_res = await client.get("/api/v1/documents")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 5. Patch title
    patch_res = await client.patch(f"/api/v1/documents/{doc_id}", json={"title": "Updated Intelligence"})
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Updated Intelligence"

    # 6. Add Highlight
    hl_res = await client.post(
        f"/api/v1/documents/{doc_id}/highlights",
        json={"page_number": 1, "selected_text": "Deep learning models", "color": "green", "note": "Important definition"}
    )
    assert hl_res.status_code == 201
    hl_id = hl_res.json()["id"]

    # 7. List Highlights
    hl_list_res = await client.get(f"/api/v1/documents/{doc_id}/highlights")
    assert hl_list_res.status_code == 200
    assert len(hl_list_res.json()) == 1

    # 8. Delete Highlight
    hl_del = await client.delete(f"/api/v1/documents/highlights/{hl_id}")
    assert hl_del.status_code == 204

    # 9. Delete Document
    del_res = await client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 204

    # Verify not found
    get_res = await client.get(f"/api/v1/documents/{doc_id}")
    assert get_res.status_code == 404
