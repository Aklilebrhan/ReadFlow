# ReadFlow — System Architecture Overview

ReadFlow is an enterprise-grade AI-powered Document Intelligence platform designed for researchers, students, and knowledge professionals. Instead of treating documents as monolithic text blobs or naive chatbot context, ReadFlow decomposes digital documents into structured semantic elements, indexes them in a hybrid vector database, and generates strictly grounded answers backed by verified page-level citations.

## Architectural Principles

ReadFlow adapts proven engineering patterns from architectural references like EchoGuide:

1. **Monorepo Structure**: Centralized codebase housing both backend (`apps/api`), frontend (`apps/web`), shared contracts (`packages/contracts`), documentation (`docs/`), and scripts (`scripts/`).
2. **Modular Monolith**: Clean domain boundaries (`documents`, `extraction`, `chunking`, `retrieval`, `chat`, `summaries`, `explanation`, `study`) without the operational overhead of microservices.
3. **Layered Separation of Concerns**: Clear demarcation of API Routing, Application Services, Domain Models, and Infrastructure Adapters.
4. **Grounded AI Retrieval-Augmented Generation (RAG)**: Answers are synthesized strictly from retrieved context chunks. If information is absent, the system explicitly refuses rather than hallucinating facts.
5. **Pluggable AI & Storage Abstraction**: Clean adapter interfaces for LLMs (OpenAI, Gemini, Ollama, and a zero-dependency local Mock mode) and Storage (Local Filesystem, S3/MinIO).

```
                      +-----------------------------+
                      |       Next.js Web App       |
                      |   (Split Reader + AI Chat)  |
                      +--------------+--------------+
                                     |  REST / OpenAPI 3.1
                                     v
                      +-----------------------------+
                      |     FastAPI Modular API     |
                      +--------------+--------------+
                                     |
    +--------------------------------+--------------------------------+
    |                                |                                |
    v                                v                                v
+------------------+       +-------------------+           +-------------------+
| Ingestion & OCR  |       | Hybrid Retrieval  |           | AI Provider Hub   |
| (PyMuPDF/Docx)   |       | (pgvector + BM25) |           | (OpenAI/Gemini/   |
+--------+---------+       +---------+---------+           |  Mock Provider)   |
         |                           |                     +---------+---------+
         v                           v                               |
+------------------------------------+-------------------------------+
|                      PostgreSQL 16 + pgvector                      |
|                  (Fallback: SQLite + Local Vector)                 |
+--------------------------------------------------------------------+
```
