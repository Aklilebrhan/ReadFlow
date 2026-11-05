# ReadFlow Contracts Package

This package maintains the shared API contracts, OpenAPI specifications, and type definitions between the ReadFlow Backend (`apps/api`) and Frontend (`apps/web`).

## Contents

- `openapi/readflow-openapi.json`: Generated OpenAPI 3.1.0 specification exported directly from the FastAPI application.
- Synchronized models for documents, RAG chat, citations, summaries, and study tools.

## Regenerating OpenAPI Spec

Run the contract generation script:

```bash
python scripts/generate_openapi.py
```
