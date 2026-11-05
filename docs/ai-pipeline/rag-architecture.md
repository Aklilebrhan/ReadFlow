# ReadFlow RAG Architecture Guide

## Pipeline Stages

ReadFlow executes a 6-stage Retrieval-Augmented Generation pipeline:

```
+-----------------------------------------------------------------------------------+
| Stage 1: Document Ingestion                                                       |
| - MIME & Size Validation (<= 50MB)                                                |
| - Original File Storage (Local / S3)                                              |
| - Text & Heading Extraction (PyMuPDF / Docx / Text)                               |
| - OCR Fallback for scanned pages                                                  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| Stage 2: Semantic Chunking                                                        |
| - Boundary-aware recursive splitting (paragraphs -> sentences -> words)           |
| - Metadata preservation: document_id, chunk_index, page_number, section_title     |
| - Configurable chunk_size (default 800) and chunk_overlap (default 150)           |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| Stage 3: Embedding Generation                                                     |
| - Provider Abstraction: Mock (384-dim), OpenAI (1536-dim), Gemini (768-dim)       |
| - Batch embedding generation (batch_size=32)                                      |
| - Storage in PostgreSQL pgvector column                                           |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| Stage 4: Hybrid Semantic Retrieval                                                |
| - Query embedding generation                                                      |
| - Dense Vector Search (cosine similarity)                                         |
| - Sparse Lexical Search (BM25 token frequency)                                    |
| - Reciprocal Rank Fusion (RRF) blending scores                                    |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| Stage 5: Grounded LLM Generation                                                  |
| - Context assembly with page-number annotations                                   |
| - Strict grounding instruction (admit ignorance if unsupported)                   |
| - Structured response with answer text and verified ChatCitation list             |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| Stage 6: Evaluation Framework                                                     |
| - Automated evaluation benchmark (tests/evaluation/dataset.json)                  |
| - Metrics: Precision@k, Recall@k, Citation Correctness, Faithfulness, Hallucination|
+-----------------------------------------------------------------------------------+
```
