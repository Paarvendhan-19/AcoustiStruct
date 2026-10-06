# AcoustiStruct 🎙️

AcoustiStruct is a dialect-aware, voice-first semantic data-capture system that converts spontaneous multilingual/local-dialect speech into validated structured records and formal documents, while preserving evidence, confidence, provenance, and human verification.

## Core Flow
**Speech → ASR → Language/Dialect Context → Semantic Normalization → Structured Extraction → Validation → Confidence → Evidence → Clarification → Database → Document**

## Features Built in MVP
- **Voice-first React Frontend:** Interactive semantic verification with glassmorphism design.
- **Provider Abstraction:** Swap between Mock, Sarvam, Whisper, Gemini, OpenAI at runtime via `.env`.
- **Dialect Normalization:** Configurable Tamil agriculture lexicon that preserves intent while standardizing output.
- **Deterministic Validation:** Schema constraints (min/max/enum) enforced deterministically, not left to LLM reasoning.
- **Field-level Evidence:** Every extracted field maps directly to its ASR transcript source segment timestamp.
- **Offline-ready Database Setup:** Asynchronous SQLite (`aiosqlite`) default configuration enables immediate local demo without heavy Docker deps.

## Getting Started

### 1. Backend (FastAPI)
The backend is set up with Python 3.11+ and FastAPI.

```bash
cd services/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_db.py
uvicorn app.main:app --reload
```
API Documentation will be at `http://localhost:8000/api/docs`.

### 2. Frontend (React + Vite)
The frontend uses React 18, Vite, and TailwindCSS.

```bash
cd apps/web
npm install
npm run dev
```
Access the application at `http://localhost:5173`.

## Architecture Details
See `execution_report.md` (or artifact output) for a full breakdown of the data models, AI pipeline, and implementation decisions.
