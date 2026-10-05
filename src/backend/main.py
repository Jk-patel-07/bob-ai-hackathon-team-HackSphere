"""
main.py — FastAPI application for the Chip Design Knowledge Assistant backend.

Routes:
  GET  /health                         — liveness + config status
  POST /ingest                         — ingest a document file
  POST /search                         — search + RAG Q&A
  GET  /categories                     — list knowledge categories
  GET  /documents/{doc_id}/sections    — list sections of a specific document

This file is intentionally thin: it delegates all logic to
rag_engine, vector_store, and document_parser modules.
"""
from __future__ import annotations

import hashlib
import logging
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .document_parser import parse_document
from .embeddings import ConfigurationError, embed_texts
from .models import (
    CategoriesResponse,
    CategoryInfo,
    DocumentInfo,
    DocumentListResponse,
    DocumentSection,
    DocumentSectionsResponse,
    HealthResponse,
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResponse,
)
from .rag_engine import answer_query
from .vector_store import (
    delete_document,
    document_exists,
    get_all_documents,
    get_categories,
    get_document_chunks,
    get_total_chunks,
    upsert_chunks,
)

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# App lifecycle
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Chip Design Knowledge Assistant starting "
        "(env=%s, watsonx_configured=%s)",
        settings.app_env,
        settings.watsonx_configured,
    )
    if not settings.watsonx_configured:
        logger.warning(
            "WATSONX_API_KEY / WATSONX_PROJECT_ID not set. "
            "Search and ingestion will fail until credentials are provided."
        )
    yield
    logger.info("Backend shutting down.")


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Chip Design Knowledge Assistant",
    description=(
        "RAG-powered knowledge base for chip design engineers. "
        "Answers questions grounded in ingested PDK, DRC, and design guideline documents."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allowed origins:
#   • Same-origin production requests (FastAPI serving the React build)
#     don't require CORS at all, but listing localhost:8000 doesn't hurt.
#   • Vite dev server on port 5173 needs CORS when running separately.
#   • MCP server (STDIO transport) does NOT make HTTP calls that need CORS.
#
# "*" is safe here because:
#   - We never use credentials=True (no cookies / Authorization headers).
#   - All endpoints are read-only queries against your own knowledge base.
#   - The app is an internal engineering tool, not a public API.
#
# If you deploy to a fixed domain, replace "*" with that domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:8000",   # Same-origin (FastAPI + static)
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"http://localhost:\d+",  # any local dev port
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    allow_credentials=False,
)


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["Utility"])
async def health() -> HealthResponse:
    """Return backend health and configuration status."""
    try:
        total = get_total_chunks()
        vs_status = "ok"
    except Exception as exc:
        logger.error("Vector store health check failed: %s", exc)
        total = 0
        vs_status = f"error: {exc}"

    return HealthResponse(
        status="ok",
        vector_store=vs_status,
        ai_provider=settings.provider,
        provider_configured=settings.provider_configured,
        watsonx_configured=settings.watsonx_configured,
        llm_model=settings.active_llm_model_id,
        embedding_model=settings.active_embedding_model_id,
        total_chunks=total,
    )


@app.post("/ingest", response_model=IngestResponse, tags=["Knowledge Base"])
async def ingest(req: IngestRequest) -> IngestResponse:
    """Parse a document file and ingest it into the vector knowledge base.

    The file must be accessible on the filesystem where the backend is running.
    Supported formats: .pdf, .md, .txt
    """
    # Validate file existence and format FIRST (before credential check)
    # so callers get a precise error even without watsonx configured.
    try:
        doc_id, doc_name, chunks = parse_document(
            file_path=req.file_path,
            category=req.category,
            doc_name=req.doc_name,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # Now check watsonx credentials — needed for the embedding step.
    current_settings = get_settings()
    if not current_settings.watsonx_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "watsonx.ai credentials are not configured. "
                "Set WATSONX_API_KEY and WATSONX_PROJECT_ID in your .env file."
            ),
        )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No text content could be extracted from the document.",
        )

    # Embed all chunks in one batched call.
    texts = [c.text for c in chunks]
    try:
        embeddings = embed_texts(texts)
    except ConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except Exception as exc:
        logger.error("Embedding call failed during ingest: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Embedding generation failed: {exc}",
        )

    metadatas = [c.metadata for c in chunks]
    n = upsert_chunks(texts, embeddings, metadatas, doc_id)

    logger.info("Ingested '%s': %d chunks stored (doc_id=%s)", doc_name, n, doc_id)
    return IngestResponse(
        doc_id=doc_id,
        doc_name=doc_name,
        category=req.category,
        chunks_created=n,
        status="ok",
    )


@app.post("/documents/upload", response_model=IngestResponse, tags=["Knowledge Base"])
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    doc_name: str | None = Form(None),
) -> IngestResponse:
    """Upload a document file (.pdf, .md, .txt, .rst) and ingest it into the vector database."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in file upload.",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".md", ".txt", ".rst"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Supported formats: .pdf, .md, .txt, .rst",
        )

    content = await file.read()
    if not content or len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    # 15 MB max upload limit
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed limit of 15 MB.",
        )

    # Compute content hash for duplicate detection
    content_hash = hashlib.sha256(content).hexdigest()[:16]

    resolved_name = (
        doc_name.strip()
        if doc_name and doc_name.strip()
        else Path(file.filename).stem.replace("_", " ").replace("-", " ").title()
    )

    # Prevent duplicate ingestion if exact document content hash exists
    if document_exists(content_hash):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document with identical content already exists in knowledge base: '{resolved_name}' (doc_id={content_hash})",
        )

    current_settings = get_settings()
    if not current_settings.watsonx_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "watsonx.ai credentials are not configured. "
                "Set WATSONX_API_KEY and WATSONX_PROJECT_ID in your .env file."
            ),
        )

    # Write to safe temporary file
    temp_dir = Path(tempfile.gettempdir())
    temp_file_path = temp_dir / f"upload_{content_hash}{ext}"

    try:
        temp_file_path.write_bytes(content)

        doc_id, name, chunks = parse_document(
            file_path=str(temp_file_path),
            category=category,
            doc_name=resolved_name,
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No text content could be extracted from the uploaded document.",
            )

        texts = [c.text for c in chunks]
        try:
            embeddings = embed_texts(texts)
        except ConfigurationError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
            )
        except Exception as exc:
            logger.error("Embedding call failed during upload: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Embedding generation failed: {exc}",
            )

        metadatas = [c.metadata for c in chunks]
        for meta in metadatas:
            meta["file_name"] = Path(file.filename).name
            meta["doc_id"] = content_hash

        n = upsert_chunks(texts, embeddings, metadatas, content_hash)

        logger.info(
            "Uploaded & ingested '%s': %d chunks stored (doc_id=%s)",
            name,
            n,
            content_hash,
        )
        return IngestResponse(
            doc_id=content_hash,
            doc_name=name,
            category=category,
            chunks_created=n,
            status="ok",
        )
    finally:
        if temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception:
                pass


@app.get("/documents", response_model=DocumentListResponse, tags=["Knowledge Base"])
async def list_documents() -> DocumentListResponse:
    """Return all stored documents with their metadata and chunk counts."""
    docs = get_all_documents()
    return DocumentListResponse(documents=docs, total_documents=len(docs))


@app.delete("/documents/{doc_id}", tags=["Knowledge Base"])
async def delete_doc(doc_id: str):
    """Remove a document and all associated text chunks from the knowledge base."""
    if not document_exists(doc_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with doc_id='{doc_id}'.",
        )
    deleted_count = delete_document(doc_id)
    return {"doc_id": doc_id, "chunks_deleted": deleted_count, "status": "ok"}



@app.post("/search", response_model=SearchResponse, tags=["Knowledge Base"])
async def search(req: SearchRequest) -> SearchResponse:
    """Search the knowledge base and return a grounded AI-generated answer.

    The answer is always grounded in retrieved document chunks. If the
    knowledge base does not contain sufficient information for the query,
    the response explicitly states so rather than generating a speculative answer.
    """
    try:
        result = answer_query(
            query=req.query,
            category=req.category,
            top_k=req.top_k,
        )
    except Exception as exc:
        logger.error("Search/RAG failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {exc}",
        )

    return result


@app.get("/categories", response_model=CategoriesResponse, tags=["Knowledge Base"])
async def categories() -> CategoriesResponse:
    """Return a summary of all document categories in the knowledge base."""
    try:
        cats = get_categories()
        total_docs = sum(c.doc_count for c in cats)
        total_chunks = sum(c.chunk_count for c in cats)
    except Exception as exc:
        logger.error("Failed to retrieve categories: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve categories: {exc}",
        )

    return CategoriesResponse(
        categories=cats,
        total_documents=total_docs,
        total_chunks=total_chunks,
    )


@app.get(
    "/documents/{doc_id}/sections",
    response_model=DocumentSectionsResponse,
    tags=["Knowledge Base"],
)
async def document_sections(doc_id: str) -> DocumentSectionsResponse:
    """Return all stored sections/chunks for a specific document."""
    raw = get_document_chunks(doc_id)
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with doc_id='{doc_id}'. "
                   "Use GET /categories to browse available documents.",
        )

    first_meta = raw[0]["metadata"]
    sections = [
        DocumentSection(
            section=item["metadata"].get("section"),
            content=item["text"],
            page=item["metadata"].get("page"),
            chunk_index=item["metadata"].get("chunk_index", i),
        )
        for i, item in enumerate(raw)
    ]

    return DocumentSectionsResponse(
        doc_id=doc_id,
        doc_name=first_meta.get("doc_name", "Unknown"),
        category=first_meta.get("category", "Uncategorised"),
        sections=sections,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Static frontend — serve the Vite build from the same process/port.
#
# The React build is output to src/backend/static/ via vite.config.js.
# All API routes (/health, /ingest, /search, /categories, /documents/…)
# are already registered above and take priority.
# Everything else falls through to the SPA index.html.
# ─────────────────────────────────────────────────────────────────────────────

_STATIC_DIR = Path(__file__).parent / "static"

if _STATIC_DIR.is_dir():
    # Serve static assets (JS, CSS, images) under /assets and root files.
    app.mount("/assets", StaticFiles(directory=_STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str, request: Request) -> FileResponse:
        """Return index.html for any path not matched by an API route.
        This enables client-side routing in the React SPA."""
        index = _STATIC_DIR / "index.html"
        return FileResponse(str(index))
else:
    logger.warning(
        "Frontend static dir not found at %s. "
        "Run `npm run build` inside src/frontend/ first.",
        _STATIC_DIR,
    )
