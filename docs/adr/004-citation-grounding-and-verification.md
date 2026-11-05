# ADR 004: Citation Grounding and Page-Level Navigation

## Status
Accepted

## Context
Standard document chatbots often hallucinate facts or invent references. For research, academic, and professional use cases, ungrounded claims are unacceptable. Users need to verify every assertion against the original document source.

## Decision
1. **Pre-Generation Retrieval**: The system never sends full documents to the LLM. It first executes hybrid search to retrieve the top $k$ relevant context chunks.
2. **Explicit Grounding System Prompt**: The language model is instructed to answer solely based on supplied context passages, cite each claim with bracketed index references (e.g. `[1]`, `[2]`), and explicitly declare when the answer cannot be found.
3. **Structured Response Contracts**: Responses return an array of `ChatCitation` objects containing:
   - `citation_id`: Numeric index matching the response text.
   - `document_id`: Target document identifier.
   - `document_title`: Human-readable document name.
   - `page_number`: Exact source page.
   - `snippet`: Extracted passage preview.
4. **Interactive UI Navigation**: In the Web reader interface, clicking any citation badge navigates the document reader to that page and highlights the relevant passage.

## Consequences
- **Positive**:
  - High user trust and verifiable answers.
  - Zero tolerance for invented page numbers.
- **Negative**:
  - Slightly larger response payload to carry citation metadata.
