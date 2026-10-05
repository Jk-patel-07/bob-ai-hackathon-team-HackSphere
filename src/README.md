# Source Code — Chip Design Knowledge Assistant

## Layout

```
src/
├── .env.example              ← Environment variable template (copy to .env)
├── requirements.txt          ← Python dependencies
├── pyproject.toml            ← pytest configuration
│
├── backend/                  ← FastAPI REST API + RAG engine
│   ├── __init__.py
│   ├── config.py             ← Centralised settings from environment variables
│   ├── models.py             ← Pydantic request & response schemas
│   ├── document_parser.py    ← PDF / Markdown / TXT section chunker
│   ├── embeddings.py         ← watsonx.ai Slate embedding wrapper
│   ├── vector_store.py       ← ChromaDB persistence & similarity search
│   ├── rag_engine.py         ← Grounded RAG retrieval & watsonx.ai Granite LLM generation
│   ├── static/               `← Built React SPA bundle served by FastAPI
│   └── main.py               ← FastAPI app routes (/health, /search, /documents, /categories)
│
├── frontend/                 ← React 18 SPA frontend (Vite + TailwindCSS)
│   ├── src/                  ← Components (Chat, Documents, KB, Sidebar, Header)
│   ├── package.json
│   └── vite.config.ts        ← Configured to output build directly into backend/static
│
├── mcp_server/               ← IBM Bob MCP integration server (STDIO transport)
│   ├── __init__.py
│   └── server.py             ← 4 MCP tools callable by IBM Bob
│
├── demo_data/                ← Synthetic semiconductor documents (SYNTHETIC DEMO DATA)
│   ├── README.md
│   ├── synthetic_pdk_design_rules.md
│   ├── synthetic_drc_standard_cells.md
│   ├── synthetic_latchup_guidelines.md
│   ├── synthetic_spice_model_notes.md
│   └── synthetic_timing_constraints.md
│
├── scripts/                  ← Utility scripts
│   └── seed_demo_data.py     ← Ingest all demo documents into ChromaDB
│
└── tests/                    ← Backend unit + integration tests (76 passed)
    ├── test_api.py
    ├── test_config.py
    ├── test_document_parser.py
    ├── test_rag.py
    └── test_vector_store.py
```

## Quick Start

```bash
# 1. Install Python dependencies
cd src
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — set WATSONX_API_KEY and WATSONX_PROJECT_ID

# 3. Start the FastAPI backend (serves API + SPA UI)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# 4. Ingest synthetic demo documents (in a separate terminal)
python scripts/seed_demo_data.py

# 5. Run tests
pytest
```

See `docs/setup-guide.md` for full setup instructions and troubleshooting details.
