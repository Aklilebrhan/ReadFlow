# ReadFlow — AI-Powered Document Intelligence Platform

[![Build Status](https://img.shields.io/badge/Build-Passing-emerald)](https://github.com/BytePhilosopher/EchoGuide)
[![Architecture](https://img.shields.io/badge/Architecture-Modular%20Monolith-indigo)](docs/architecture/overview.md)
[![Vector Engine](https://img.shields.io/badge/Vector%20Storage-pgvector%20%2F%20PostgreSQL%2016-blue)](docs/adr/002-pgvector-and-hybrid-retrieval.md)
[![License](https://img.shields.io/badge/License-MIT-slate)](LICENSE)

ReadFlow is an enterprise-grade AI-powered document intelligence and interactive reading platform. Instead of naive text dumps or hallucinating chatbots, ReadFlow decomposes PDFs, DOCX, and Markdown documents into structured semantic chunks, stores vector embeddings in PostgreSQL using `pgvector`, and generates strictly grounded answers with verifiable page-level citations.

---

## Key Features

- **Document Ingestion & Multi-Format Support**:
  - High-performance PDF extraction via PyMuPDF (`fitz`) with heading hierarchy detection.
  - Optical Character Recognition (OCR) fallback for scanned pages.
  - Native support for Word (`.docx`), Markdown (`.md`), and plain text (`.txt`).
  - Asynchronous background pipeline with live status tracking (`Uploaded` → `Extracting` → `Processing` → `Indexing` → `Ready`).

- **Grounded AI Document Chat**:
  - Strict grounding in retrieved document chunks before generating model answers.
  - Verified page citations (e.g., `[1] Page 2`) linking directly to the source passage.
  - Interactive citation jumping: clicking a citation scrolls the document reader to that exact page.
  - Explicit refusal when questions are absent from document context (zero hallucination).
  - Multi-document cross-synthesis across collections.

- **Intelligent Hierarchical Summarization**:
  - Quick, detailed executive, section-by-section, and key points summaries.
  - Map-reduce hierarchical summarizer for long documents exceeding 3,000 words to avoid context window degradation.

- **In-Situ Document Explanation**:
  - Highlight any text passage in the reader to trigger on-the-fly simplifications, technical deep-dives, definitions, and real-world analogies.

- **Study & Research Workspace**:
  - Interactive 3D flip card flashcard decks.
  - Comprehension quizzes with instant answer feedback and rationales.
  - Extracted terminology glossary and structured study notes.
  - Highlight saving and annotation management.

---

## Architectural Reference & Monorepo Structure

ReadFlow follows clean modular monolith patterns inspired by [EchoGuide](https://github.com/BytePhilosopher/EchoGuide):

```
readflow/
├── apps/
│   ├── api/                           # Python 3.12 FastAPI Modular Monolith
│   │   ├── app/
│   │   │   ├── main.py                # App entrypoint, lifespan, CORS, middleware
│   │   │   ├── core/                  # Settings, structured logging, domain exceptions
│   │   │   ├── shared/                # Database (SQLAlchemy/pgvector), storage, AI provider hub
│   │   │   └── modules/               # Domain modules (documents, chunking, retrieval, chat, etc.)
│   │   ├── tests/                     # Unit, integration, and RAG evaluation tests
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── web/                           # Next.js 14 App Router Web Application
│       ├── src/
│       │   ├── app/                   # App Router pages (/dashboard, /documents/[id], /chat, /study)
│       │   ├── components/            # UI components (Button, Badge, Dialog, Input) and AppShell
│       │   ├── features/              # Dashboard, Reader, Chat, Summaries, Study workspaces
│       │   └── lib/                   # API client, types, utilities
│       ├── package.json
│       └── Dockerfile
│
├── packages/
│   └── contracts/
│       └── openapi/
│           └── readflow-openapi.json  # OpenAPI 3.1.0 specification
│
├── docs/
│   ├── architecture/                  # System architecture, C4 models, modular monolith guide
│   ├── adr/                           # Architecture Decision Records (ADR 001 - ADR 005)
│   ├── ai-pipeline/                   # RAG architecture, chunking strategies, evaluation metrics
│   ├── testing/                       # Testing pyramid and guide
│   └── deployment/                    # Production deployment instructions
│
├── scripts/
│   ├── generate_openapi.py            # Generates OpenAPI contract specification
│   ├── evaluate_rag.py                # Standalone RAG evaluation runner (Precision@k, Recall@k, etc.)
│   ├── seed_sample_docs.py            # Seeds database with sample research papers
│   └── test_system.py                 # End-to-end integration verification suite
│
├── docker-compose.yml                 # Multi-container orchestration (db, api, web)
├── .env.example                       # Documented environment template
└── README.md
```

---

## AI Provider Architecture

ReadFlow implements an adapter pattern via `BaseChatProvider` and `BaseEmbeddingProvider`:

- **Mock Provider (Default)**: Fully functional out of the box with zero external API keys! Generates deterministic 384-dimensional vector embeddings, grounded citations, summaries, and flashcards. Clearly labelled as simulated mode.
- **OpenAI**: Configurable for `gpt-4o`, `gpt-4o-mini`, and `text-embedding-3-small`.
- **Google Gemini**: Supports `gemini-1.5-flash`, `gemini-1.5-pro`, and `text-embedding-004`.
- **Ollama**: Local open-weights LLMs and embeddings.

Switch providers simply by setting the `AI_PROVIDER` environment variable:

```env
AI_PROVIDER=mock      # Zero-cost local mode
# AI_PROVIDER=openai  # With OPENAI_API_KEY
# AI_PROVIDER=gemini  # With GEMINI_API_KEY
```

---

## Quick Start with Docker Compose

1. **Clone repository**:
   ```bash
   git clone https://github.com/BytePhilosopher/EchoGuide.git readflow
   cd readflow
   ```

2. **Copy environment variables**:
   ```bash
   cp .env.example .env
   ```

3. **Launch with Docker Compose**:
   ```bash
   docker compose up --build -d
   ```

4. **Access the application**:
   - Web Workspace: `http://localhost:3000`
   - FastAPI Docs: `http://localhost:8000/docs`
   - Healthcheck: `http://localhost:8000/health`

---

## Local Development Without Docker

### 1. Backend Setup

```bash
cd apps/api
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Seed Sample Research Documents

```bash
python scripts/seed_sample_docs.py
```

### 3. Run Automated Tests & RAG Evaluation

```bash
# Run backend pytest suite (12 passed in 0.4s)
pytest apps/api/tests -v

# Run RAG Evaluation Benchmark
python scripts/evaluate_rag.py

# Run End-to-End System Verification
python scripts/test_system.py
```

### 4. Start Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```

Visit `http://localhost:3000` to interact with ReadFlow.

---

## RAG Evaluation Benchmark

ReadFlow includes an evaluation framework measuring:
- **Precision@k**: Ratio of relevant chunks retrieved in the top $k$.
- **Recall@k**: Ratio of ground truth keywords retrieved.
- **Citation Correctness**: Verified against ground truth source pages.
- **Faithfulness Score**: Context grounding ratio.
- **Hallucination Rate**: Unsupported claim detection.

Run the evaluation runner:
```bash
python scripts/evaluate_rag.py
```

---

## License

ReadFlow is open-source software licensed under the MIT License.
