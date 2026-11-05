# ReadFlow Deployment Guide

ReadFlow is fully containerized with Docker and Docker Compose.

## Architecture Topology

The standard deployment consists of three services:
1. **`db`**: PostgreSQL 16 container with `pgvector` pre-installed (`pgvector/pgvector:pg16`).
2. **`api`**: Python 3.12 FastAPI service with PyMuPDF, OCR capabilities, and SQLAlchemy 2.0.
3. **`web`**: Next.js 14 App Router production standalone server.

## Quick Start with Docker Compose

1. Clone repository and copy environment configuration:
   ```bash
   cp .env.example .env
   ```
2. Build and start services:
   ```bash
   docker compose up --build -d
   ```
3. Check container status:
   ```bash
   docker compose ps
   ```
4. Access the web interface at `http://localhost:3000` and the API Swagger docs at `http://localhost:8000/docs`.

## Local Development Without Docker

1. **Start Backend**:
   ```bash
   cd apps/api
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
2. **Start Frontend**:
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```
3. Open `http://localhost:3000`.
