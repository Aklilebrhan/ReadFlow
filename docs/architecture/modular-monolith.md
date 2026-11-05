# Modular Monolith Architecture

ReadFlow implements a **Modular Monolith** architecture. This avoids the high operational complexity, distributed transactions, and network latency of microservices, while enforcing strict domain separation and maintainability.

## Module Structure

Each domain module in `apps/api/app/modules/` follows a uniform architectural blueprint:

```
modules/<domain>/
├── models.py      # SQLAlchemy persistence entities
├── schemas.py     # Pydantic v2 validation contracts & DTOs
├── repository.py  # Data access abstractions (async queries)
├── service.py     # Domain orchestration & business logic
└── router.py      # HTTP endpoints and routing
```

### Module Boundaries

1. **`documents`**: Document metadata, collections management, highlights, and processing state machines.
2. **`extraction`**: Format-specific parsers (`PDFExtractor` via PyMuPDF, `DocxExtractor`, `TextExtractor`, and OCR fallbacks).
3. **`chunking`**: Sentence and boundary-aware chunking algorithms preserving page numbers and section headings.
4. **`embeddings`**: Batch vector generation with dimension validation.
5. **`ingestion`**: Multi-stage state machine orchestrator coordinating the ingestion lifecycle.
6. **`retrieval`**: Dense vector search (pgvector), sparse lexical search (BM25), and Reciprocal Rank Fusion (RRF).
7. **`chat`**: Grounded conversational AI orchestrator adhering to zero-hallucination policies and generating verified citations.
8. **`summaries`**: Hierarchical map-reduce summarizer for long documents.
9. **`explanation`**: In-situ passage explanations and glossary extraction.
10. **`study`**: Interactive learning material generators (flashcards, quizzes, study notes).

## Layer Hierarchy

```
[ HTTP Presentation Layer (FastAPI Routers) ]
                      │
                      ▼
[ Application Layer (Services & Ingestion Orchestrators) ]
                      │
                      ▼
[ Domain Layer (Models, Chunking, Evaluation, Grounding) ]
                      │
                      ▼
[ Shared Infrastructure (SQLAlchemy, pgvector, Storage, AI Providers) ]
```
