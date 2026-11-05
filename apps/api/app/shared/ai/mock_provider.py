import hashlib
import math
from typing import List, Dict, Any, Optional
from app.shared.ai.base import (
    BaseChatProvider,
    BaseEmbeddingProvider,
    ChatCompletionResult,
    ChatCitation,
    TokenUsage
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministic, zero-dependency embedding provider for local development and testing."""

    def __init__(self, dimension: int = 384):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def _hash_to_vector(self, text: str) -> List[float]:
        """Generates a reproducible, pseudo-semantic normalized vector using text hashing."""
        vec = [0.0] * self._dim
        words = text.lower().split()
        if not words:
            vec[0] = 1.0
            return vec

        for word in words:
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            for i in range(4):
                idx = (h >> (i * 16)) % self._dim
                val = (((h >> (i * 16 + 8)) & 0xFF) / 127.5) - 1.0
                vec[idx] += val

        # Normalize vector to unit length
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        else:
            vec[0] = 1.0
        return vec

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_to_vector(t) for t in texts]

    async def embed_query(self, query: str) -> List[float]:
        return self._hash_to_vector(query)


class MockChatProvider(BaseChatProvider):
    """Deterministic Mock LLM provider for zero-API-cost local runs and unit testing."""

    async def generate_rag_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None
    ) -> ChatCompletionResult:
        logger.info("MockChatProvider: Processing query with %d retrieved chunks", len(context_chunks))

        # Grounding check: verify that retrieved chunks actually contain relevant query context
        import re
        stop_words = {"what", "this", "that", "from", "with", "have", "about", "your", "does", "been", "where", "when", "which"}
        query_tokens = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2 and w not in stop_words]

        has_relevant_content = False
        if context_chunks and query_tokens:
            min_matches = 2 if len(query_tokens) >= 2 else 1
            for chunk in context_chunks:
                chunk_text = chunk.get("text", "").lower()
                matched = [t for t in query_tokens if t in chunk_text]
                if len(matched) >= min_matches:
                    has_relevant_content = True
                    break

        if not context_chunks or not has_relevant_content:
            return ChatCompletionResult(
                answer="I could not find information in the provided document(s) to answer your question. Please verify your query or upload documents containing relevant content.",
                citations=[],
                token_usage=TokenUsage(prompt_tokens=45, completion_tokens=32, total_tokens=77, estimated_cost_usd=0.0),
                model="mock-rag-v1",
                provider="mock",
                is_mock=True
            )

        citations: List[ChatCitation] = []
        findings = []

        for idx, chunk in enumerate(context_chunks[:4], start=1):
            doc_id = chunk.get("document_id", "unknown")
            doc_title = chunk.get("document_title", "Document")
            page_num = chunk.get("page_number", 1)
            chunk_id = chunk.get("chunk_id", str(idx))
            text = chunk.get("text", "").strip()
            score = chunk.get("score")

            snippet = text[:180] + "..." if len(text) > 180 else text
            citations.append(
                ChatCitation(
                    citation_id=idx,
                    document_id=doc_id,
                    document_title=doc_title,
                    page_number=page_num,
                    chunk_id=chunk_id,
                    snippet=snippet,
                    relevance_score=score
                )
            )
            findings.append(f"- **Finding {idx}** (Page {page_num}): {snippet} [{idx}]")

        answer_text = (
            f"[Development Mock Mode — Simulated Grounded Response]\n\n"
            f"Based on your document '{citations[0].document_title}', here is the synthesized answer to **'{query}'**:\n\n"
            + "\n".join(findings)
            + f"\n\n*This answer was retrieved from {len(citations)} source passages across the document.*"
        )

        return ChatCompletionResult(
            answer=answer_text,
            citations=citations,
            token_usage=TokenUsage(
                prompt_tokens=len(query.split()) + sum(len(c.snippet.split()) for c in citations),
                completion_tokens=len(answer_text.split()),
                total_tokens=len(query.split()) + len(answer_text.split()),
                estimated_cost_usd=0.0
            ),
            model="mock-rag-v1",
            provider="mock",
            is_mock=True
        )

    async def generate_summary(
        self,
        text_content: str,
        summary_type: str = "quick",
        instructions: Optional[str] = None
    ) -> str:
        words = text_content.split()
        snippet = " ".join(words[:120])

        if summary_type == "detailed":
            return (
                f"[Development Mock Mode — Detailed Summary]\n\n"
                f"### Executive Overview\n{snippet}...\n\n"
                f"### Key Sections & Methodology\n"
                f"1. **Core Problem**: The document addresses strategic challenges and document comprehension inefficiencies.\n"
                f"2. **Approach**: Synthesizes structured data extraction with retrieval-augmented generation.\n"
                f"3. **Outcomes**: Demonstrates enhanced precision, verified citations, and reduced hallucinations.\n\n"
                f"### Conclusions & Recommendations\n"
                f"The findings suggest adopting modular document processing pipelines to scale knowledge retrieval."
            )
        elif summary_type == "key_points":
            return (
                f"[Development Mock Mode — Key Points]\n\n"
                f"- **Core Theme**: High-throughput intelligent document ingestion and retrieval.\n"
                f"- **Architecture**: Decoupled ingestion, boundary-aware chunking, and hybrid search.\n"
                f"- **Grounding**: Strict adherence to cited passages with zero hallucination policy.\n"
                f"- **Context Overview**: {snippet}..."
            )
        elif summary_type == "chapters":
            return (
                f"[Development Mock Mode — Section-by-Section Summary]\n\n"
                f"#### Section 1: Introduction & Problem Scope\nIntroduces the background context and objectives.\n\n"
                f"#### Section 2: Methodology & Implementation\nDetails the technical architecture, data processing, and evaluation metrics.\n\n"
                f"#### Section 3: Evaluation & Findings\nReports quantitative benchmarks, precision@k metrics, and practical impact."
            )
        else:  # quick
            return (
                f"[Development Mock Mode — Quick Summary]\n\n"
                f"This document provides a comprehensive analysis of the subject matter. "
                f"Key discussion revolves around: {snippet}... "
                f"Overall, it presents actionable insights grounded in empirical observations."
            )

    async def explain_passage(
        self,
        passage: str,
        explanation_type: str = "simple"
    ) -> str:
        passage_trimmed = passage.strip()[:200]
        if explanation_type == "simple":
            return (
                f"[Development Mock Mode — Simple Explanation]\n\n"
                f"**In plain English:** This passage is saying that: *'{passage_trimmed}'* "
                f"essentially means we are breaking down complex information so it is easy to read and understand without technical jargon."
            )
        elif explanation_type == "technical":
            return (
                f"[Development Mock Mode — Technical Analysis]\n\n"
                f"**Technical Breakdown:** The statement refers to algorithmic principles and structural semantics. "
                f"Specifically, it operates on: *'{passage_trimmed}'*, enforcing formal constraints and optimization invariants."
            )
        elif explanation_type == "define":
            return (
                f"[Development Mock Mode — Term Definitions]\n\n"
                f"**Key Concepts Identified:**\n"
                f"- **Primary Subject**: The fundamental entity described in the selected passage.\n"
                f"- **Operational Context**: The surrounding parameters governing the behavior."
            )
        elif explanation_type == "example":
            return (
                f"[Development Mock Mode — Practical Example]\n\n"
                f"**Real-world Analogy:** Consider an index at the back of a textbook: instead of scanning 500 pages, "
                f"you look up the specific term and go directly to page 42."
            )
        elif explanation_type == "translate":
            return (
                f"[Development Mock Mode — Translation / Paraphrase]\n\n"
                f"**Paraphrased Interpretation:** '{passage_trimmed}'"
            )
        else:
            return f"[Development Mock Mode — Main Idea]\n\nThe central idea is: {passage_trimmed}"

    async def generate_study_materials(
        self,
        text_content: str,
        material_type: str = "flashcards"
    ) -> Dict[str, Any]:
        words = [w for w in text_content.split() if len(w) > 4][:10]

        if material_type == "flashcards":
            return {
                "material_type": "flashcards",
                "items": [
                    {
                        "front": f"What is the core premise of {words[0] if words else 'the document'}?",
                        "back": f"The core premise establishes structured retrieval and verified citations for document intelligence."
                    },
                    {
                        "front": f"How is {words[1] if len(words) > 1 else 'chunking'} applied?",
                        "back": "Content is segmented into semantically coherent blocks preserving paragraph and sentence boundaries."
                    },
                    {
                        "front": "What ensures answer grounding in the RAG pipeline?",
                        "back": "Context chunks are retrieved prior to generation, and assertions must cite supporting document pages."
                    }
                ]
            }
        elif material_type == "quiz":
            return {
                "material_type": "quiz",
                "items": [
                    {
                        "question": "What is the primary benefit of chunking with overlap?",
                        "options": [
                            "Prevents semantic context loss at chunk boundaries",
                            "Doubles the size of the database",
                            "Encrypts document data",
                            "Speeds up network transfers"
                        ],
                        "correct_index": 0,
                        "explanation": "Overlap guarantees phrases crossing split boundaries remain intact in at least one chunk."
                    },
                    {
                        "question": "How are citations validated in ReadFlow?",
                        "options": [
                            "By guessing page numbers",
                            "By linking generated assertions directly to retrieved chunk metadata",
                            "By external search engines",
                            "Random sampling"
                        ],
                        "correct_index": 1,
                        "explanation": "Citations map explicitly to source chunk IDs and page numbers stored in the vector database."
                    }
                ]
            }
        else:  # key_terms
            return {
                "material_type": "key_terms",
                "items": [
                    {
                        "term": "Retrieval-Augmented Generation (RAG)",
                        "definition": "An AI framework combining vector search with language models to produce grounded answers.",
                        "context": "Used to retrieve relevant document chunks before prompting the LLM."
                    },
                    {
                        "term": "Semantic Chunking",
                        "definition": "Splitting text at natural paragraph and sentence boundaries rather than arbitrary character counts.",
                        "context": "Preserves contextual integrity for vector embedding."
                    },
                    {
                        "term": "Reciprocal Rank Fusion (RRF)",
                        "definition": "A hybrid search fusion algorithm combining dense vector similarity with sparse BM25 scores.",
                        "context": "Ensures both keyword matches and conceptual semantics are captured."
                    }
                ]
            }
