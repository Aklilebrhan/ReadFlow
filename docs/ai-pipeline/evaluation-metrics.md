# RAG Evaluation Framework

ReadFlow includes an automated evaluation suite to benchmark and optimize retrieval quality, grounding, and citation correctness.

## Benchmark Dataset

Located at `apps/api/tests/evaluation/dataset.json`, the dataset contains:
- Real research queries across academic papers.
- Ground truth passage keywords.
- Ground truth source page numbers.
- Unanswerable control queries to test graceful refusal behavior.

## Measured Metrics

1. **Precision@k**:
   $$\text{Precision@}k = \frac{\text{Relevant chunks retrieved in top } k}{k}$$
2. **Recall@k**:
   $$\text{Recall@}k = \frac{\text{Expected keywords found in top } k}{\text{Total expected keywords}}$$
3. **Citation Correctness**:
   Fraction of citations whose `page_number` matches the ground truth page:
   $$\text{Citation Correctness} = \frac{\sum \mathbb{I}(\text{citation.page} = \text{ground\_truth.page})}{|\text{citations}|}$$
4. **Faithfulness Score**:
   Measures lexical and semantic grounding of generated claims against the retrieved context passages.
5. **Hallucination Rate**:
   Defined as $1.0 - \text{Faithfulness Score}$.

## Running the Benchmark

```bash
python scripts/evaluate_rag.py
```
