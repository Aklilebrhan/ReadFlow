# ADR 002: PostgreSQL with pgvector and Reciprocal Rank Fusion Hybrid Search

## Status
Accepted

## Context
A Document Intelligence platform requires semantic vector retrieval to handle conceptual similarities. However, vector search alone often struggles with exact keyword matching (e.g. acronyms, proper nouns, version numbers, code symbols). Furthermore, maintaining a dedicated vector database (such as Pinecone, Qdrant, or Milvus) alongside a relational database creates dual-write consistency issues and extra infrastructure.

## Decision
1. We choose **PostgreSQL 16** with the **pgvector** extension as the unified relational and vector storage engine.
2. In production, chunk embeddings are stored in native `vector(384)` or `vector(1536)` columns with HNSW or IVFFlat index support.
3. For retrieval, we implement **Hybrid Retrieval** combining:
   - Dense vector cosine similarity search.
   - Sparse lexical BM25 token-matching search.
   - **Reciprocal Rank Fusion (RRF)**:
     $$\text{RRF Score}(d) = \alpha \cdot \frac{1}{60 + \text{rank}_v(d)} + (1 - \alpha) \cdot \frac{1}{60 + \text{rank}_k(d)}$$
4. We provide an automated in-memory cosine fallback for local SQLite development and test environments, guaranteeing 100% test isolation without requiring an external PostgreSQL daemon.

## Consequences
- **Positive**:
  - Single database to back up, migrate, and secure.
  - ACID transactions across documents, metadata, chunks, and embeddings.
  - High retrieval accuracy combining conceptual and keyword matching.
- **Negative**:
  - Requires `pgvector` extension to be enabled in PostgreSQL environments.
