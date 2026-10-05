# 🚀 Chip Design Knowledge Assistant

> **IBM Bob Hackathon Submission — Track: AI**

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | TODO: Enter Team Name |
| **Track** | AI |
| **Team Lead** | TODO: Enter Team Lead Name — TODO: Enter Lead Email |
| **Members** | TODO: Enter Member 1, TODO: Enter Member 2, TODO: Enter Member 3 |

---

## 🎯 Problem Statement

Semiconductor design engineers spend significant technical effort searching through lengthy PDK (Process Design Kit) documentation, DRC/LVS rulebooks, latchup guidelines, and timing constraint manuals. Information is frequently scattered across multi-page PDFs and Markdown files.

Context switching between EDA tools and documentation slows down physical layout and verification work. Furthermore, standard generic LLMs risk hallucinating numeric design tolerances (such as minimum metal pitch or guard ring spacing), which can result in costly silicon re-spins if relied upon without exact document verification.

---

## 💡 Solution

The **Chip Design Knowledge Assistant** provides a domain-specific retrieval-augmented generation (RAG) system built on IBM watsonx.ai, FastAPI, ChromaDB, and PyMuPDF.

The system is designed to minimize hallucinations by grounding answers in retrieved documents and returning an explicit insufficient-information response when supporting evidence is unavailable.

Additionally, an **IBM Bob Model Context Protocol (MCP)** STDIO server allows developers and engineers to query chip design specifications directly from their IDE assistant using standard MCP tools (`search_knowledge_base`, `get_document_sections`, `list_ingested_documents`, `check_backend_status`).

---

## ✨ Key Features

- **Grounded AI Q&A with Citation Deduplication:** Retrieves top relevant chunks from vector storage, passes only verified context to watsonx.ai, and deduplicates source document citations down to section level.
- **Strict Low-Confidence Fallback:** Automatically returns a standard insufficient-information message when document similarity scores fall below the configured threshold (default `0.30`) or when LLM analysis indicates context lack.
- **Multi-Format Ingestion Pipeline:** Ingests PDF, Markdown, and TXT files, automatically generating section-aware chunks using LangChain text splitters and PyMuPDF.
- **IBM Bob MCP Server:** Full MCP STDIO tool suite allowing IBM Bob to trigger RAG search and document queries seamlessly inside the developer workspace.
- **Document & Knowledge Base Management:** REST API endpoints (`GET /documents`, `POST /documents/upload`, `DELETE /documents/{doc_id}`) paired with a React frontend to inspect, upload, filter, and remove documents dynamically.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.11+, TypeScript, HTML, CSS |
| **Frameworks & Libraries** | FastAPI, React 18, Vite, TailwindCSS, PyMuPDF, LangChain Text Splitters, Pydantic |
| **IBM Technologies** | IBM watsonx.ai, IBM Bob (Model Context Protocol / MCP) |
| **Vector Store** | ChromaDB (Persistent storage with cosine similarity indexing) |
| **Testing & Tools** | pytest (76 unit/integration tests passing), Uvicorn |

---

## 📁 Repository Structure

```
├── src/                  # All source code
│   ├── backend/          # FastAPI REST API, RAG engine, document parser, ChromaDB wrapper
│   ├── mcp_server/       # IBM Bob MCP STDIO integration server
│   ├── frontend/         # React SPA frontend (built into backend/static)
│   ├── demo_data/        # Synthetic chip design demo documents
│   ├── scripts/          # Seed and setup scripts
│   └── tests/            # 76 backend unit & integration tests
├── docs/                 # Detailed documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   ├── live-demo-url.txt # Live deployment status
│   └── demo-video-link.txt # Link to demo video
├── presentation/         # Slide deck location
└── submission.yaml       # Hackathon submission metadata
```

---

## ⚡ How to Run

```bash
# 1. Clone the repository
git clone https://github.com/Jk-patel-07/bob-ai-hackathon-team-HackSphere.git
cd bob-ai-hackathon-team-HackSphere

# 2. Configure environment
cp src/.env.example src/.env
# Edit src/.env with your WATSONX_API_KEY and WATSONX_PROJECT_ID

# 3. Install dependencies and start server
cd src
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# 4. Ingest synthetic demo documents
python scripts/seed_demo_data.py

# 5. Access the application
# Open browser at http://localhost:8000
```

To run test suites:
```bash
# Backend pytest suite (76 tests)
cd src && pytest

# Frontend build check
cd src/frontend && npm run build
```

---

## 🖥️ Demo

| Artifact | Location / Status |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) (NOT DEPLOYED — Run locally) |
| 🖼️ Screenshots | [01 Home Dashboard](demo/screenshots/01-home-dashboard.png) • [02 Grounded Query](demo/screenshots/02-grounded-query.png) • [03 Citation Result](demo/screenshots/03-citation-result.png) • [04 Knowledge Base](demo/screenshots/04-knowledge-base.png) • [05 Documents](demo/screenshots/05-documents.png) |
| 📊 Presentation | [See presentation/](presentation/) |

---

## ⚠️ Known Limitations

- **Hackathon Prototype / MVP:** Built as a single-tenant hackathon prototype focused on core RAG reliability and MCP integration.
- **Synthetic Demo Data:** Ships with synthetic semiconductor specifications (`synthetic_pdk_design_rules.md`, `synthetic_drc_standard_cells.md`, etc.) for demonstration purposes rather than real proprietary foundry PDK rules.
- **Authentication:** Authentication is currently open for single-tenant local execution. Production enterprise deployment would require OAuth2/OIDC integration.

---

## 🏅 What We're Most Proud Of

We are most proud of our strict anti-hallucination grounding architecture and seamless dual-interface capability. Engineers can search, browse documents, and query grounded chip design insights either visually through the web application or directly in their IDE via IBM Bob MCP integration without leaving their workflow.
