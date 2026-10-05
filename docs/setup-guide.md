# Setup Guide — Chip Design Knowledge Assistant

> **This setup guide provides complete instructions to install, configure, run, and test the application.**

---

## Prerequisites

Ensure you have the following installed on your system:

- [x] **Python 3.11+**
- [x] **Node.js 18+ & npm** (Required only for building frontend SPA)
- [x] **Git**
- [x] **Google Gemini API Key** (or IBM Cloud watsonx.ai credentials)

---

## Environment Variables

Copy `.env.example` to `src/.env` (or root `.env`):

```bash
cp src/.env.example src/.env
```

| Variable | Description | Required | Default / Sample Value |
|---|---|---|---|
| `AI_PROVIDER` | Active AI provider (`gemini` or `watsonx`) | No | `gemini` |
| `GEMINI_API_KEY` | Google Gemini API Key | Yes (if `AI_PROVIDER=gemini`) | `your_gemini_api_key_here` |
| `GEMINI_MODEL` | Gemini text generation model | No | `gemini-2.5-flash` |
| `GEMINI_EMBEDDING_MODEL` | Gemini text embedding model | No | `text-embedding-004` |
| `WATSONX_API_KEY` | IBM Cloud IAM API Key for watsonx.ai | Yes (if `AI_PROVIDER=watsonx`) | `your_watsonx_api_key_here` |
| `WATSONX_PROJECT_ID` | IBM watsonx.ai Project ID | Yes (if `AI_PROVIDER=watsonx`) | `your_watsonx_project_id_here` |
| `WATSONX_URL` | Regional IBM Cloud ML endpoint | No | `https://us-south.ml.cloud.ibm.com` |
| `WATSONX_LLM_MODEL_ID` | Model ID for watsonx answer generation | No | `ibm/granite-13b-instruct-v2` |
| `WATSONX_EMBEDDING_MODEL_ID` | Model ID for watsonx vector embeddings | No | `ibm/slate-125m-english-rtrvr` |
| `APP_PORT` | FastAPI server port | No | `8000` |
| `CHROMA_PERSIST_DIR` | ChromaDB persistence directory | No | `./chroma_data` |
| `CHROMA_COLLECTION_NAME` | ChromaDB collection name | No | `chip_design_knowledge` |
| `BACKEND_URL` | Backend URL used by MCP server | No | `http://localhost:8000` |
| `RAG_TOP_K` | Number of chunks to retrieve per search | No | `5` |
| `RAG_MIN_SIMILARITY` | Minimum similarity score threshold | No | `0.30` |

---

## Installation & Running

### 1. Clone the Repository

```bash
git clone https://github.com/Jk-patel-07/bob-ai-hackathon-team-HackSphere.git
cd bob-ai-hackathon-team-HackSphere
```

### 2. Set Up Virtual Environment & Install Dependencies

```bash
# Navigate to source directory
cd src

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Build Frontend SPA (Optional if static assets already present)

```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY (or WATSONX_API_KEY & WATSONX_PROJECT_ID)
```

### 5. Start the FastAPI Backend Server

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

The application will be available at: `http://localhost:8000`

### 6. Seed Synthetic Demo Data

In a second terminal window (with virtualenv activated in `src/`):

```bash
python scripts/seed_demo_data.py
```

This ingests 5 synthetic semiconductor spec files (`synthetic_pdk_design_rules.md`, `synthetic_drc_standard_cells.md`, `synthetic_latchup_guidelines.md`, `synthetic_spice_model_notes.md`, `synthetic_timing_constraints.md`) into ChromaDB.

---

## Running IBM Bob MCP Server

To run the MCP server for IBM Bob integration:

```bash
# Ensure backend server is running on http://localhost:8000
cd src
python -m mcp_server.server
```

---

## Running Tests

### Backend Unit & Integration Tests

```bash
cd src
pytest
```
*Expected output:* `81 passed`

### Frontend Build Verification

```bash
cd src/frontend
npm run build
```
*Expected output:* Vite production build completes cleanly.

---

## Troubleshooting Matrix

| Issue / Error | Root Cause | Resolution |
|---|---|---|
| `Gemini API key is not configured` | Missing or invalid `GEMINI_API_KEY` | Set `GEMINI_API_KEY` in `src/.env`. Get a key from https://aistudio.google.com/ |
| `watsonx.ai credentials are not configured` | Missing `WATSONX_API_KEY` when `AI_PROVIDER=watsonx` | Set `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` in `src/.env` or switch `AI_PROVIDER=gemini`. |
| `404 Not Found` when loading `http://localhost:8000` | Frontend static bundle missing in `src/backend/static` | Run `npm run build` inside `src/frontend` to build the SPA into `src/backend/static`. |
| MCP Server connection refused | FastAPI backend is not running on `http://localhost:8000` | Start backend server with `uvicorn backend.main:app --port 8000` before starting MCP server. |
| `0 chunks returned` in search | Vector database is empty | Run `python scripts/seed_demo_data.py` or upload documents via the Documents tab in UI. |
