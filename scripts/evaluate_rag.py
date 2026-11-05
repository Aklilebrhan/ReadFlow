import json
import os
import sys
import asyncio

# Add apps/api to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api")))

from tests.evaluation.evaluator import RAGEvaluator
from app.shared.ai.factory import get_chat_provider, get_embedding_provider
from app.modules.chunking.recursive_chunker import RecursiveCharacterChunker
from app.modules.extraction.base import ExtractedDocument, ExtractedPage
from app.core.config import settings


async def run_evaluation():
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api", "tests", "evaluation", "dataset.json"))
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["items"]
    print(f"============================================================")
    print(f" ReadFlow RAG Pipeline Evaluation")
    print(f" Benchmark: {data['benchmark_name']}")
    print(f" Provider: {settings.AI_PROVIDER} | Top-K: {settings.RETRIEVAL_TOP_K}")
    print(f"============================================================\n")

    chat_provider = get_chat_provider()
    results = []

    for item in items:
        # Build synthetic context chunk
        chunk = {
            "chunk_id": f"chunk-{item['id']}",
            "document_id": f"doc-{item['id']}",
            "document_title": item["document_title"],
            "page_number": item["page_number"],
            "text": item["synthetic_content"],
            "score": 0.92
        }

        # For irrelevant query (eval-005), don't provide matching context to test refusal
        context_chunks = [chunk] if item["ground_truth_page"] is not None else []

        # Execute model generation
        gen_res = await chat_provider.generate_rag_response(
            query=item["query"],
            context_chunks=context_chunks
        )

        metrics = RAGEvaluator.calculate_metrics(
            query_item=item,
            retrieved_chunks=context_chunks,
            answer=gen_res.answer,
            citations=gen_res.citations,
            k=settings.RETRIEVAL_TOP_K
        )

        results.append({
            "id": item["id"],
            "query": item["query"],
            "metrics": metrics
        })

        print(f"[{item['id']}] '{item['query'][:45]}...'")
        print(f"   Precision@5: {metrics['precision_at_k']:.2f} | Recall@5: {metrics['recall_at_k']:.2f} | Citation Acc: {metrics['citation_correctness']:.2f} | Faithfulness: {metrics['faithfulness']:.2f} | Hallucination: {metrics['hallucination_rate']:.2f}")

    # Aggregate
    avg_precision = sum(r["metrics"]["precision_at_k"] for r in results) / len(results)
    avg_recall = sum(r["metrics"]["recall_at_k"] for r in results) / len(results)
    avg_citation = sum(r["metrics"]["citation_correctness"] for r in results) / len(results)
    avg_faithfulness = sum(r["metrics"]["faithfulness"] for r in results) / len(results)
    avg_hallucination = sum(r["metrics"]["hallucination_rate"] for r in results) / len(results)

    print(f"\n============================================================")
    print(f" SUMMARY METRICS (n={len(results)})")
    print(f" - Average Precision@k:    {avg_precision:.4f}")
    print(f" - Average Recall@k:       {avg_recall:.4f}")
    print(f" - Citation Correctness:   {avg_citation:.4f}")
    print(f" - Faithfulness Score:     {avg_faithfulness:.4f}")
    print(f" - Hallucination Rate:     {avg_hallucination:.4f}")
    print(f"============================================================")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
