"""
server.py — Chip Design Knowledge Assistant MCP server (MCP SDK v2).

This is the IBM Bob integration layer. It exposes four tools over the
MCP STDIO transport so that Bob can call the knowledge backend directly
from the IDE chat interface.

Tools:
  search_knowledge_base    — Ask a chip design question (main RAG Q&A)
  ingest_document          — Add a document to the knowledge base
  list_document_categories — Browse what's in the knowledge base
  get_document_sections    — Inspect a specific document's content

Transport: STDIO (runs as a subprocess started by Bob IDE)
SDK:       mcp >= 2.0  (MCPServer + run_stdio_async)
Config:    .bob/mcp.json in the project root

Environment variables (all read at runtime, never hardcoded):
  BACKEND_URL — FastAPI backend base URL (default: http://localhost:8000)

Usage (Bob starts this automatically via mcp.json):
  python src/mcp_server/server.py
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer

# ─────────────────────────────────────────────────────────────────────────────
# Logging — write to stderr so it doesn't contaminate the STDIO MCP stream
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [MCP] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000").rstrip("/")

# ─────────────────────────────────────────────────────────────────────────────
# MCPServer instance
# ─────────────────────────────────────────────────────────────────────────────

mcp = MCPServer(
    name="chip-knowledge",
    version="1.0.0",
    description=(
        "Chip Design Knowledge Assistant — grounded Q&A over PDK, DRC, "
        "design guidelines, SPICE model notes, and timing documents."
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _backend_get(path: str, params: dict | None = None) -> dict[str, Any]:
    url = f"{BACKEND_URL}{path}"
    with httpx.Client(timeout=60.0) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


def _backend_post(path: str, body: dict) -> dict[str, Any]:
    url = f"{BACKEND_URL}{path}"
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=body)
        resp.raise_for_status()
        return resp.json()


# ─────────────────────────────────────────────────────────────────────────────
# Result formatters
# ─────────────────────────────────────────────────────────────────────────────

def _format_search_response(data: dict) -> str:
    lines: list[str] = []
    answer = data.get("answer", "No answer returned.")
    sufficient = data.get("sufficient_context", False)
    model = data.get("model_used", "unknown")
    retrieved = data.get("retrieved_chunks", 0)

    lines.append(f"## Answer\n\n{answer}\n")

    if not sufficient:
        lines.append(
            "> ⚠️ **Insufficient context**: The knowledge base did not contain "
            "enough relevant information to answer this question confidently. "
            "Consider ingesting additional documents.\n"
        )

    citations = data.get("citations", [])
    if citations:
        lines.append("## Sources\n")
        for i, cit in enumerate(citations, 1):
            doc = cit.get("doc_name", "Unknown")
            cat = cit.get("category", "")
            section = cit.get("section") or "General"
            page = cit.get("page")
            score = cit.get("similarity_score", 0)
            page_str = f", page {page}" if page else ""
            lines.append(
                f"**[{i}]** {doc} ({cat}) | Section: *{section}*{page_str} "
                f"| Similarity: {score:.2f}"
            )
            snippet = cit.get("chunk_text", "")[:200]
            lines.append(f"  > {snippet}…\n")

    lines.append(f"---\n*Model: {model} | Chunks used: {retrieved}*")
    return "\n".join(lines)


def _format_ingest_response(data: dict) -> str:
    return (
        f"✅ **Document ingested successfully**\n\n"
        f"- **Name:** {data.get('doc_name', 'Unknown')}\n"
        f"- **Category:** {data.get('category', 'Unknown')}\n"
        f"- **Doc ID:** `{data.get('doc_id', 'Unknown')}`\n"
        f"- **Chunks stored:** {data.get('chunks_created', 0)}\n\n"
        f"The document is now searchable via `search_knowledge_base`."
    )


def _format_categories_response(data: dict) -> str:
    cats = data.get("categories", [])
    total_docs = data.get("total_documents", 0)
    total_chunks = data.get("total_chunks", 0)

    if not cats:
        return (
            "The knowledge base is currently empty.\n"
            "Use `ingest_document` to add PDK, DRC, or design guideline documents."
        )

    lines = [
        f"## Knowledge Base Contents\n",
        f"**{total_docs} document(s)** | **{total_chunks} chunks** indexed\n",
        "| Category | Documents | Chunks |",
        "|---|---|---|",
    ]
    for cat in cats:
        lines.append(
            f"| {cat['name']} | {cat['doc_count']} | {cat['chunk_count']} |"
        )
    return "\n".join(lines)


def _format_sections_response(data: dict) -> str:
    doc_name = data.get("doc_name", "Unknown")
    category = data.get("category", "")
    sections = data.get("sections", [])

    if not sections:
        return f"No content found for document '{doc_name}'."

    lines = [f"## {doc_name}\n*Category: {category}*\n"]
    for sec in sections:
        heading = sec.get("section") or "General"
        page = sec.get("page")
        page_str = f" *(page {page})*" if page else ""
        lines.append(f"### {heading}{page_str}\n")
        lines.append(sec.get("content", "") + "\n")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Tools (MCP v2 @mcp.tool() decorator)
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool(
    description=(
        "Search the chip design knowledge base and get a grounded AI-generated answer. "
        "Use this tool whenever an engineer asks a question about PDK rules, DRC guidelines, "
        "design constraints, SPICE model usage, latch-up prevention, or any chip design topic. "
        "The answer is always backed by citations from ingested documents. "
        "If the knowledge base lacks sufficient information, the tool explicitly says so "
        "rather than guessing."
    )
)
def search_knowledge_base(
    query: str,
    category: str | None = None,
    top_k: int = 5,
) -> str:
    """
    Args:
        query:    The chip design question to answer (natural language).
        category: Optional category filter (e.g. 'PDK', 'DRC'). None = all.
        top_k:    Maximum number of source chunks to retrieve (default 5).
    """
    logger.info("search_knowledge_base: query=%r category=%r top_k=%d", query, category, top_k)
    body: dict[str, Any] = {"query": query, "top_k": top_k}
    if category:
        body["category"] = category

    try:
        data = _backend_post("/search", body)
        return _format_search_response(data)
    except httpx.ConnectError:
        return (
            f"❌ **Backend not reachable** at {BACKEND_URL}.\n\n"
            "Please start the FastAPI backend first:\n"
            "```\ncd src && uvicorn backend.main:app --reload\n```"
        )
    except httpx.HTTPStatusError as exc:
        detail = ""
        try:
            detail = exc.response.json().get("detail", "")
        except Exception:
            pass
        return f"❌ **Backend error {exc.response.status_code}**: {detail or exc.response.text[:200]}"
    except Exception as exc:
        logger.exception("search_knowledge_base failed")
        return f"❌ **Unexpected error**: {exc}"


@mcp.tool(
    description=(
        "Add a new document (PDF or Markdown) to the chip design knowledge base. "
        "Use this when an engineer provides a PDK spec, DRC rule deck, design guideline, "
        "or application note that should be searchable. "
        "The document is chunked, embedded, and stored persistently."
    )
)
def ingest_document(
    file_path: str,
    category: str,
    doc_name: str | None = None,
) -> str:
    """
    Args:
        file_path: Absolute or relative path to the file (.pdf, .md, or .txt).
        category:  Knowledge category (e.g. 'PDK', 'DRC', 'Design Guidelines').
        doc_name:  Optional human-readable name. Defaults to the filename.
    """
    logger.info("ingest_document: file=%r category=%r", file_path, category)
    body: dict[str, Any] = {"file_path": file_path, "category": category}
    if doc_name:
        body["doc_name"] = doc_name

    try:
        data = _backend_post("/ingest", body)
        return _format_ingest_response(data)
    except httpx.ConnectError:
        return (
            f"❌ **Backend not reachable** at {BACKEND_URL}.\n\n"
            "Please start the FastAPI backend first:\n"
            "```\ncd src && uvicorn backend.main:app --reload\n```"
        )
    except httpx.HTTPStatusError as exc:
        detail = ""
        try:
            detail = exc.response.json().get("detail", "")
        except Exception:
            pass
        return f"❌ **Backend error {exc.response.status_code}**: {detail or exc.response.text[:200]}"
    except Exception as exc:
        logger.exception("ingest_document failed")
        return f"❌ **Unexpected error**: {exc}"


@mcp.tool(
    description=(
        "List all document categories currently in the chip design knowledge base, "
        "along with document and chunk counts. Use this to understand what knowledge "
        "is available before asking a question or to confirm a document was ingested."
    )
)
def list_document_categories() -> str:
    """No arguments required."""
    logger.info("list_document_categories called")
    try:
        data = _backend_get("/categories")
        return _format_categories_response(data)
    except httpx.ConnectError:
        return (
            f"❌ **Backend not reachable** at {BACKEND_URL}.\n\n"
            "Please start the FastAPI backend: `uvicorn backend.main:app --reload`"
        )
    except Exception as exc:
        logger.exception("list_document_categories failed")
        return f"❌ **Unexpected error**: {exc}"


@mcp.tool(
    description=(
        "Retrieve the full content of a specific document from the knowledge base, "
        "organised by section. Use this when an engineer wants to read the source text "
        "of a specific rule, section, or document in full rather than getting a Q&A answer."
    )
)
def get_document_sections(doc_id: str) -> str:
    """
    Args:
        doc_id: The document ID (returned by ingest_document or visible in search citations).
    """
    logger.info("get_document_sections: doc_id=%r", doc_id)
    try:
        data = _backend_get(f"/documents/{doc_id}/sections")
        return _format_sections_response(data)
    except httpx.ConnectError:
        return (
            f"❌ **Backend not reachable** at {BACKEND_URL}.\n\n"
            "Please start the FastAPI backend: `uvicorn backend.main:app --reload`"
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return (
                f"❌ **Document not found**: No document with ID `{doc_id}` exists.\n"
                "Use `list_document_categories` to browse available documents."
            )
        detail = ""
        try:
            detail = exc.response.json().get("detail", "")
        except Exception:
            pass
        return f"❌ **Backend error {exc.response.status_code}**: {detail or exc.response.text[:200]}"
    except Exception as exc:
        logger.exception("get_document_sections failed")
        return f"❌ **Unexpected error**: {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio
    logger.info("Chip Knowledge MCP server starting (backend=%s)", BACKEND_URL)
    asyncio.run(mcp.run_stdio_async())
