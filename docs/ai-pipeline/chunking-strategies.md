# Document Chunking Strategies

ReadFlow provides modular chunking strategies via the strategy registry in `app/modules/chunking/factory.py`.

## 1. Recursive Character Chunker (`RecursiveCharacterChunker`)

The default chunking algorithm (`CHUNK_STRATEGY=recursive`).
- **Splitting Order**:
  1. Paragraph boundaries (`\n\n`)
  2. Line boundaries (`\n`)
  3. Sentence terminators (`.`, `!`, `?`)
  4. Word spaces (` `)
- **Context Preservation**:
  - Automatically identifies section headings by font size analysis during extraction.
  - Attaches `page_number` and active `section_title` to every emitted chunk.
  - Enforces `chunk_overlap` (default 150 characters) to ensure concepts spanning split boundaries are never lost.

## 2. Sentence Boundary Chunker (`SentenceBoundaryChunker`)

Activated via `CHUNK_STRATEGY=sentence`.
- Strictly enforces that sentences are **never broken across chunk boundaries**.
- Accumulates complete sentences until adding another would exceed `CHUNK_SIZE`.
- Retains the preceding sentence as the overlap context for the following chunk.
- Highly suitable for legal documents, medical literature, and contracts where sentence fragmenting could alter clause semantics.
