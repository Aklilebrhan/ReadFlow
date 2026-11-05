# ReadFlow Testing Strategy

ReadFlow implements a testing pyramid covering unit, integration, RAG quality, and end-to-end API workflows.

## Backend Test Architecture

Tests reside in `apps/api/tests/`:

1. **`test_documents.py`**:
   - Tests document upload, background ingestion triggering, status progression polling, patch renaming, and highlights management.
2. **`test_extraction.py`**:
   - Generates in-memory synthetic PDFs via PyMuPDF (`fitz`), Markdown documents, and DOCX files.
   - Asserts page count, text fidelity, and heading extraction.
3. **`test_chunking.py`**:
   - Tests `RecursiveCharacterChunker` and `SentenceBoundaryChunker`.
   - Validates character size limits, overlap carryover, and page metadata persistence.
4. **`test_retrieval.py`**:
   - Tests cosine similarity calculations and Reciprocal Rank Fusion hybrid search.
5. **`test_chat.py`**:
   - Verifies grounded question answering, page citations, token usage metrics, and refusal behavior for questions absent from context.
6. **`test_summaries.py`**:
   - Tests quick, detailed, and hierarchical map-reduce summarization.
7. **`test_study.py`**:
   - Tests flashcard deck generation, multiple choice quizzes, and key terms glossary.

## Running Tests

```bash
# Run backend pytest suite
cd apps/api
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing
```
