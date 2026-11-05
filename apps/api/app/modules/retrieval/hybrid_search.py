from typing import List, Dict, Any


def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]],
    keyword_results: List[Dict[str, Any]],
    alpha: float = 0.6,
    k_constant: int = 60,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Combines dense semantic vector hits and sparse keyword matches using Reciprocal Rank Fusion.
    Score = alpha * (1 / (k + rank_v)) + (1 - alpha) * (1 / (k + rank_k))
    """
    merged: Dict[str, Dict[str, Any]] = {}

    for rank, item in enumerate(vector_results, start=1):
        cid = item["chunk_id"]
        if cid not in merged:
            merged[cid] = {**item, "rrf_score": 0.0, "vector_rank": rank, "keyword_rank": None}
        merged[cid]["rrf_score"] += alpha * (1.0 / (k_constant + rank))

    for rank, item in enumerate(keyword_results, start=1):
        cid = item["chunk_id"]
        if cid not in merged:
            merged[cid] = {**item, "rrf_score": 0.0, "vector_rank": None, "keyword_rank": rank}
        else:
            merged[cid]["keyword_rank"] = rank
        merged[cid]["rrf_score"] += (1.0 - alpha) * (1.0 / (k_constant + rank))

    fused_list = list(merged.values())
    fused_list.sort(key=lambda x: x["rrf_score"], reverse=True)

    # Normalize fused score for client presentation
    for item in fused_list:
        item["score"] = round(item["rrf_score"] * 100, 3)
        item["search_type"] = "hybrid"

    return fused_list[:top_k]
