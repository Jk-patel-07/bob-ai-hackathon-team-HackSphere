# Solution Overview — Chip Design Knowledge Assistant

## What We Built

The **Chip Design Knowledge Assistant** is a domain-focused knowledge management and retrieval-augmented generation (RAG) platform. It enables semiconductor engineering teams to ingest design documentation (PDFs, Markdown, TXT) and query engineering rules through a web UI or directly within IBM Bob via Model Context Protocol (MCP) tools.

The system is designed to minimize hallucinations by grounding answers in retrieved documents and returning an insufficient-information response when supporting evidence is unavailable.

> ⚠️ **Note on Demo Data:** All sample semiconductor files provided in `src/demo_data/` are **SYNTHETIC DEMO DATA** generated for testing and demonstration purposes, not actual proprietary semiconductor foundry rules.

---

## How It Works

```
[User Query / IBM Bob] ──► [FastAPI / RAG Engine] ──► [ChromaDB Vector Store]
                                    │                         │
                                    ▼                         ▼
                       [Check Similarity Threshold]    [Retrieve Top-K Chunks]
                                    │
                        ┌───────────┴───────────┐
                        ▼                       ▼
               [Score < Min Similarity]  [Score >= Min Similarity]
                        │                       │
                        ▼                       ▼
              [Return Fallback Msg]    [Prompt + Context to AI Provider]
                                                │ (Gemini or watsonx)
                                                ▼
                                       [Grounded Answer + Citations]
```

1. **Document Ingestion & Chunking:** Documents (PDFs, Markdown, TXT) uploaded via the frontend or API are parsed using PyMuPDF and LangChain heading-aware splitters into section-level text chunks.
2. **Vectorization & Indexing:** Chunks are vectorized using the configured AI provider's embedding model (`AI_PROVIDER=gemini` with `text-embedding-004` or `AI_PROVIDER=watsonx` with `ibm/slate-125m-english-rtrvr`) and persisted in ChromaDB alongside document and category metadata.
3. **Similarity Search & Thresholding:** When a query arrives, ChromaDB performs cosine vector search to retrieve top candidate chunks (default `RAG_TOP_K=5`). If highest similarity score is below `RAG_MIN_SIMILARITY` (default `0.30`), the RAG engine immediately returns the standard insufficient-information message without making an LLM call.
4. **Grounded Answer Generation:** If chunks pass threshold, they are formatted into a strict system prompt and sent to the active AI provider (configured model: `gemini-2.5-flash` or `ibm/granite-13b-instruct-v2`). The model synthesizes an answer using *only* the retrieved context.
5. **Citation Deduplication & Fallback Handlers:** Output citations are deduplicated down to exact document titles and sections. If the LLM generates an insufficient context token (e.g. `[INSUFFICIENT_CONTEXT]`), the API cleanly converts it into the user-facing fallback response.
6. **Dual Protocol Access:** Users can query the assistant via the React Web UI or directly inside IBM Bob using the custom MCP STDIO server tools (`search_knowledge_base`, `get_document_sections`, `list_ingested_documents`, `check_backend_status`).

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **AI Provider Abstraction (`AI_PROVIDER`)** | Supports Google Gemini API (`AI_PROVIDER=gemini`) as a fully operational alternative alongside IBM watsonx.ai (`AI_PROVIDER=watsonx`), preventing credential dependency blockers. |
| **Similarity Thresholding (Default 0.30)** | Prevents passing irrelevant chunks to the LLM, avoiding hallucinated answers when no relevant specification document exists. |
| **Citation Deduplication at Backend Level** | Ensures users receive clear, unique source document references rather than repetitive list entries for multi-chunk matches. |
| **Model Context Protocol (MCP) Integration** | Exposes knowledge base operations to IBM Bob as native tools, allowing engineers to query design rules directly from their IDE assistant. |
| **PyMuPDF + LangChain Heading Splitter** | Preserves section heading hierarchy during PDF and Markdown chunking, maintaining critical context for technical rules. |
| **Single-Port FastAPI SPA Serving** | FastAPI serves both API endpoints and the compiled React production static bundle from `src/backend/static`, simplifying execution and local deployment. |

---

## AI Technologies Used

- **IBM Bob (MCP Protocol):** Integrated via Python Model Context Protocol (`mcp` package v2) STDIO transport, exposing 4 server tools that IBM Bob calls during interactive coding sessions.
- **Google Gemini API (Active Provider):** Configurable text generation (`gemini-2.5-flash`) and vector embeddings (`text-embedding-004`) via `google-genai` Python SDK.
- **IBM watsonx.ai (Supported Alternative):** Configurable text generation (`ibm/granite-13b-instruct-v2`) and vector embeddings (`ibm/slate-125m-english-rtrvr`) via `ibm-watsonx-ai` SDK.
