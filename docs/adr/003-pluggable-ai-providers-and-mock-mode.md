# ADR 003: Pluggable AI Provider Architecture and Local Mock Mode

## Status
Accepted

## Context
Tightly coupling ReadFlow to a single commercial LLM vendor (e.g. OpenAI) creates vendor lock-in, exposes the application to API pricing fluctuations, and makes local automated testing costly and fragile when developers or CI systems lack paid credentials.

## Decision
1. We implement an **Adapter Pattern** with abstract interfaces:
   - `BaseChatProvider`: generates grounded RAG responses, summaries, and study materials.
   - `BaseEmbeddingProvider`: generates dense vector representations.
2. We support OpenAI, Google Gemini, Ollama, and a dedicated **Mock AI Provider**.
3. **Mock Mode Requirements**:
   - Must be fully functional out of the box with zero external API keys.
   - Generates deterministic 384-dimensional vector embeddings using token hashing.
   - Generates realistic, grounded answers citing actual retrieved chunks.
   - Must clearly identify itself as `[Development Mock Mode]` in headers and metadata so users never mistake it for genuine AI output.
4. Provider selection is configured exclusively through the `AI_PROVIDER` environment variable.

## Consequences
- **Positive**:
  - Developers can run and verify the entire system offline and without paid API keys.
  - Smooth switching to state-of-the-art models (OpenAI, Gemini, Ollama) by setting environment variables.
  - Zero sensitive API keys committed to git or exposed to the frontend.
