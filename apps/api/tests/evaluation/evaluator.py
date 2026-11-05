import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class RAGEvaluator:
    """Evaluates retrieval quality, grounding, citation fidelity, and hallucination rates."""

    @staticmethod
    def precision_at_k(retrieved_chunks: List[Dict[str, Any]], expected_keywords: List[str], k: int = 5) -> float:
        if not expected_keywords:
            return 1.0  # Irrelevant query, expecting no positive chunks or handled gracefully
        if not retrieved_chunks:
            return 0.0

        top_chunks = retrieved_chunks[:k]
        relevant_count = 0
        for chunk in top_chunks:
            text = chunk.get("text", "").lower()
            if any(kw.lower() in text for kw in expected_keywords):
                relevant_count += 1

        return relevant_count / len(top_chunks)

    @staticmethod
    def recall_at_k(retrieved_chunks: List[Dict[str, Any]], expected_keywords: List[str], k: int = 5) -> float:
        if not expected_keywords:
            return 1.0
        if not retrieved_chunks:
            return 0.0

        top_chunks = retrieved_chunks[:k]
        found_keywords = set()
        for chunk in top_chunks:
            text = chunk.get("text", "").lower()
            for kw in expected_keywords:
                if kw.lower() in text:
                    found_keywords.add(kw.lower())

        return len(found_keywords) / len(expected_keywords)

    @staticmethod
    def citation_correctness(citations: List[Any], ground_truth_page: Optional[int]) -> float:
        if ground_truth_page is None:
            # For ungroundable queries, expecting 0 citations
            return 1.0 if len(citations) == 0 else 0.0
        if not citations:
            return 0.0

        correct_citations = sum(1 for c in citations if getattr(c, "page_number", None) == ground_truth_page or c.get("page_number") == ground_truth_page)
        return correct_citations / len(citations)

    @staticmethod
    def faithfulness_score(answer: str, context_chunks: List[Dict[str, Any]]) -> float:
        """Estimates faithfulness by measuring claim grounding against retrieved text."""
        if not answer.strip():
            return 0.0
        if "could not find information" in answer.lower():
            return 1.0  # Perfect refusal faithfulness

        sentences = [s.strip() for s in re.split(r'[.!?]', answer) if len(s.strip()) > 15]
        if not sentences:
            return 1.0

        context_text = " ".join(c.get("text", "").lower() for c in context_chunks)
        supported = 0

        for sentence in sentences:
            tokens = [t.lower() for t in re.findall(r'\w+', sentence) if len(t) > 3]
            if not tokens:
                supported += 1
                continue
            matched = sum(1 for t in tokens if t in context_text)
            if (matched / len(tokens)) > 0.4:
                supported += 1

        return round(supported / len(sentences), 4)

    @staticmethod
    def calculate_metrics(
        query_item: Dict[str, Any],
        retrieved_chunks: List[Dict[str, Any]],
        answer: str,
        citations: List[Any],
        k: int = 5
    ) -> Dict[str, float]:
        expected_kws = query_item.get("expected_passage_keywords", [])
        gt_page = query_item.get("ground_truth_page")

        p_at_k = RAGEvaluator.precision_at_k(retrieved_chunks, expected_kws, k=k)
        r_at_k = RAGEvaluator.recall_at_k(retrieved_chunks, expected_kws, k=k)
        cit_corr = RAGEvaluator.citation_correctness(citations, gt_page)
        faith = RAGEvaluator.faithfulness_score(answer, retrieved_chunks)
        hallucination = round(max(0.0, 1.0 - faith), 4)

        return {
            "precision_at_k": round(p_at_k, 4),
            "recall_at_k": round(r_at_k, 4),
            "citation_correctness": round(cit_corr, 4),
            "faithfulness": faith,
            "hallucination_rate": hallucination
        }
