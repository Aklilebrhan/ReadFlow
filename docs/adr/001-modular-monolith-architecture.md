# ADR 001: Modular Monolith Architecture

## Status
Accepted

## Context
ReadFlow requires high developer velocity, transactional consistency across document ingestion, extraction, and vector storage, and simple deployment. Choosing a distributed microservices architecture early would introduce network overhead, operational complexity, inter-service serialization, and distributed debugging burdens without justification.

## Decision
We adopt a **Modular Monolith** architecture pattern organized within a monorepo:
1. Modules are structured cleanly inside `apps/api/app/modules/`.
2. Each domain module owns its schemas, models, services, repositories, and routes.
3. Dependencies between modules are unidirectional through explicit service layer contracts.
4. Database transactions are isolated and managed per background task or request.

## Consequences
- **Positive**:
  - Simple deployment via a single Docker container.
  - Zero network latency between ingestion, chunking, and vector storage.
  - Effortless local testability and automated CI/CD.
  - Modules can still be extracted into dedicated microservices in the future if a specific domain requires independent auto-scaling.
- **Negative**:
  - Requires code review discipline to prevent circular imports between modules.
