# ADR 005: Hierarchical Map-Reduce Summarization for Long Documents

## Status
Accepted

## Context
Academic papers, legal briefs, and textbooks often exceed 20 to 100 pages (10,000 to 50,000 words). Sending entire long documents in a single LLM prompt causes:
1. Context window exhaustion or heavy token truncation.
2. "Lost in the Middle" attention degradation where models ignore central arguments.
3. Prohibitive latency and token costs.

## Decision
We implement a **Hierarchical Map-Reduce Summarizer**:
1. Documents under 3,000 words are summarized in a single pass.
2. Documents exceeding 3,000 words trigger the multi-stage map-reduce workflow:
   - **Map Stage**: The document is segmented by section or page clusters. Each segment is summarized in parallel or sequence, capturing page ranges and section titles.
   - **Reduce Stage**: The intermediate section digests are concatenated and synthesized into a master executive summary.
3. The UI presents both the master executive overview and an interactive section-by-section breakdown accordion.

## Consequences
- **Positive**:
  - Scales gracefully to documents of hundreds of pages.
  - Retains nuanced findings across every chapter.
  - Predictable token budgets per model call.
