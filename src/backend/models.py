"""
models.py — Pydantic request/response schemas for the backend API.

These are the data contracts between:
  - FastAPI routes ↔ callers (MCP server, tests, optional web UI)
  - Internal backend layers
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Ingestion
# ─────────────────────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    """Request to ingest a single document file into the knowledge base."""

    file_path: str = Field(..., description="Absolute or relative path to the document file (PDF or Markdown).")
    category: str = Field(..., description="Knowledge category, e.g. 'PDK', 'DRC', 'Design Guidelines'.")
    doc_name: str | None = Field(None, description="Human-readable document name. Defaults to filename.")


class IngestResponse(BaseModel):
    """Result of an ingestion operation."""

    doc_id: str = Field(..., description="Unique identifier assigned to this document.")
    doc_name: str
    category: str
    chunks_created: int = Field(..., description="Number of text chunks stored in the vector database.")
    status: str = Field(..., description="'ok' on success.")


# ─────────────────────────────────────────────────────────────────────────────
# Search / Q&A
# ─────────────────────────────────────────────────────────────────────────────

class Citation(BaseModel):
    """A single source reference backing part of an answer."""

    doc_id: str
    doc_name: str
    category: str
    section: str | None = Field(None, description="Section heading from the source document, if available.")
    page: int | None = Field(None, description="Page number in the source PDF, if available.")
    chunk_text: str = Field(..., description="The verbatim chunk text that supported the answer.")
    similarity_score: float = Field(..., description="Cosine similarity score [0–1] between query and chunk.")


class SearchRequest(BaseModel):
    """A knowledge-base query."""

    query: str = Field(..., min_length=3, description="Natural-language question or search term.")
    category: str | None = Field(None, description="Optional category filter (e.g. 'DRC'). None = search all.")
    top_k: int = Field(5, ge=1, le=20, description="Maximum number of source chunks to retrieve.")


class SearchResponse(BaseModel):
    """Result of a knowledge-base search / RAG Q&A."""

    query: str
    answer: str = Field(
        ...,
        description=(
            "Grounded answer synthesised from retrieved document chunks. "
            "If the knowledge base does not contain sufficient information the answer "
            "will explicitly say so rather than hallucinating."
        ),
    )
    citations: list[Citation] = Field(default_factory=list)
    retrieved_chunks: int = Field(..., description="Number of chunks actually used to build the answer.")
    sufficient_context: bool = Field(
        ...,
        description="True when retrieved evidence meets the minimum similarity threshold.",
    )
    model_used: str = Field(..., description="watsonx.ai model ID used for generation.")


# ─────────────────────────────────────────────────────────────────────────────
# Categories
# ─────────────────────────────────────────────────────────────────────────────

class CategoryInfo(BaseModel):
    name: str
    doc_count: int
    chunk_count: int


class CategoriesResponse(BaseModel):
    categories: list[CategoryInfo]
    total_documents: int
    total_chunks: int


# ─────────────────────────────────────────────────────────────────────────────
# Document sections
# ─────────────────────────────────────────────────────────────────────────────

class DocumentSection(BaseModel):
    section: str | None
    content: str
    page: int | None
    chunk_index: int


class DocumentSectionsResponse(BaseModel):
    doc_id: str
    doc_name: str
    category: str
    sections: list[DocumentSection]


# ─────────────────────────────────────────────────────────────────────────────
# Document listing
# ─────────────────────────────────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    """Metadata summary for a single stored document."""

    doc_id: str
    doc_name: str
    category: str
    chunk_count: int
    file_name: str | None = None
    created_at: str | None = None
    status: str = "indexed"


class DocumentListResponse(BaseModel):
    """List of all indexed documents in the knowledge base."""

    documents: list[DocumentInfo]
    total_documents: int


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    vector_store: str
    ai_provider: str = "gemini"
    provider_configured: bool = False
    watsonx_configured: bool = False
    llm_model: str
    embedding_model: str
    total_chunks: int

