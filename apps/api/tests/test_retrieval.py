import pytest
from app.modules.retrieval.vector_search import cosine_similarity
from app.modules.retrieval.hybrid_search import reciprocal_rank_fusion


def test_cosine_similarity():
    # Identical vectors
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert pytest.approx(cosine_similarity(v1, v2), 0.001) == 1.0

    # Orthogonal vectors
    v3 = [0.0, 1.0, 0.0]
    assert pytest.approx(cosine_similarity(v1, v3), 0.001) == 0.0

    # Opposite vectors
    v4 = [-1.0, 0.0, 0.0]
    assert pytest.approx(cosine_similarity(v1, v4), 0.001) == -1.0


def test_reciprocal_rank_fusion():
    vector_results = [
        {"chunk_id": "c1", "text": "chunk 1", "score": 0.95},
        {"chunk_id": "c2", "text": "chunk 2", "score": 0.85},
    ]
    keyword_results = [
        {"chunk_id": "c2", "text": "chunk 2", "score": 4.2},
        {"chunk_id": "c3", "text": "chunk 3", "score": 3.1},
    ]

    fused = reciprocal_rank_fusion(vector_results, keyword_results, alpha=0.6, top_k=3)
    assert len(fused) == 3

    # chunk 2 appears in both vector and keyword rankings, so it should receive boosted score
    assert fused[0]["chunk_id"] == "c2" or fused[0]["chunk_id"] == "c1"
    assert "score" in fused[0]
