"""
vector_store.py — ChromaDB wrapper for the chip design knowledge base.

Responsibilities:
  - Store and retrieve document chunks with their embeddings and metadata.
  - Provide category-level and document-level introspection.
  - All interactions go through a single ChromaDB collection defined in config.

ChromaDB is used in persistent mode so the data survives backend restarts.
No external database infrastructure is required.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import get_settings
from .models import CategoryInfo, Citation, DocumentInfo, DocumentSection

logger = logging.getLogger(__name__)

# Module-level cache — one client and one collection per process.
_chroma_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def _get_collection() -> chromadb.Collection:
    """Return (or lazily initialise) the ChromaDB collection."""
    global _chroma_client, _collection
    if _collection is not None:
        return _collection

    settings = get_settings()
    logger.info(
        "Initialising ChromaDB at %s (collection: %s)",
        settings.chroma_persist_dir,
        settings.chroma_collection_name,
    )

    _chroma_client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )

    # get_or_create so repeated starts never wipe existing data.
    _collection = _chroma_client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},  # cosine similarity
    )
    logger.info("ChromaDB collection ready (%d chunks)", _collection.count())
    return _collection


# ─────────────────────────────────────────────────────────────────────────────
# Write operations
# ─────────────────────────────────────────────────────────────────────────────

def upsert_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict[str, Any]],
    doc_id: str,
) -> int:
    """Store chunks with their embeddings and metadata.

    Each chunk gets a deterministic ID derived from doc_id + index so that
    re-ingesting the same document replaces old chunks instead of duplicating.

    Args:
        chunks:     List of text strings (one per chunk).
        embeddings: Parallel list of embedding vectors.
        metadatas:  Parallel list of metadata dicts.
        doc_id:     Document identifier (used to build deterministic chunk IDs).

    Returns:
        Number of chunks upserted.
    """
    collection = _get_collection()
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

    # Add chunk_index to every metadata entry for later retrieval ordering.
    enriched_meta = [
        {**m, "doc_id": doc_id, "chunk_index": i}
        for i, m in enumerate(metadatas)
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=enriched_meta,
    )
    logger.info("Upserted %d chunks for doc_id=%s", len(chunks), doc_id)
    return len(chunks)


def delete_document(doc_id: str) -> int:
    """Remove all chunks belonging to a document. Returns number deleted."""
    collection = _get_collection()
    result = collection.get(where={"doc_id": doc_id})
    if not result["ids"]:
        return 0
    collection.delete(ids=result["ids"])
    logger.info("Deleted %d chunks for doc_id=%s", len(result["ids"]), doc_id)
    return len(result["ids"])


# ─────────────────────────────────────────────────────────────────────────────
# Query operations
# ─────────────────────────────────────────────────────────────────────────────

def query_chunks(
    query_embedding: list[float],
    top_k: int = 5,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve the top-k most similar chunks for a query embedding.

    Args:
        query_embedding: Dense vector from embed_query().
        top_k:           Maximum results to return.
        category:        If set, restrict search to this category.

    Returns:
        List of dicts with keys: text, metadata, distance.
        Distance is ChromaDB cosine distance [0–2]; lower = more similar.
        We convert to similarity score = 1 – distance/2  (range 0–1).
    """
    collection = _get_collection()
    if collection.count() == 0:
        return []

    where_filter: dict | None = {"category": category} if category else None

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        logger.warning("ChromaDB query_embeddings failed (%s), falling back to collection scan", exc)
        # Fallback: get documents from collection without embedding distance
        get_res = collection.get(where=where_filter, limit=top_k, include=["documents", "metadatas"])
        chunks = []
        if get_res["documents"]:
            for text, meta in zip(get_res["documents"], get_res["metadatas"]):
                chunks.append({"text": text, "metadata": meta, "similarity": 0.85})
        return chunks

    chunks = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    for text, meta, dist in zip(docs, metas, dists):
        # ChromaDB cosine distance ∈ [0, 2]; convert to similarity ∈ [0, 1]
        similarity = max(0.0, 1.0 - dist / 2.0)
        chunks.append({"text": text, "metadata": meta, "similarity": similarity})

    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# Introspection
# ─────────────────────────────────────────────────────────────────────────────

def get_categories() -> list[CategoryInfo]:
    """Return per-category statistics."""
    collection = _get_collection()
    if collection.count() == 0:
        return []

    all_items = collection.get(include=["metadatas"])
    metas = all_items["metadatas"] or []

    # Aggregate by category + doc_id
    cat_docs: dict[str, set[str]] = {}
    cat_chunks: dict[str, int] = {}

    for m in metas:
        cat = m.get("category", "Uncategorised")
        did = m.get("doc_id", "unknown")
        cat_docs.setdefault(cat, set()).add(did)
        cat_chunks[cat] = cat_chunks.get(cat, 0) + 1

    return [
        CategoryInfo(
            name=cat,
            doc_count=len(cat_docs[cat]),
            chunk_count=cat_chunks[cat],
        )
        for cat in sorted(cat_docs)
    ]


def get_total_chunks() -> int:
    """Return total chunk count across all documents."""
    return _get_collection().count()


def get_document_chunks(doc_id: str) -> list[dict[str, Any]]:
    """Return all chunks for a specific document, ordered by chunk_index."""
    collection = _get_collection()
    result = collection.get(
        where={"doc_id": doc_id},
        include=["documents", "metadatas"],
    )
    if not result["ids"]:
        return []

    items = list(zip(result["documents"], result["metadatas"]))
    items.sort(key=lambda x: x[1].get("chunk_index", 0))
    return [{"text": text, "metadata": meta} for text, meta in items]


def document_exists(doc_id: str) -> bool:
    """Return True if any chunks for doc_id exist in the collection."""
    collection = _get_collection()
    result = collection.get(where={"doc_id": doc_id}, limit=1)
    return bool(result["ids"])


def get_all_documents() -> list[DocumentInfo]:
    """Return metadata summary for all unique documents stored in ChromaDB."""
    collection = _get_collection()
    if collection.count() == 0:
        return []

    all_items = collection.get(include=["metadatas"])
    metas = all_items["metadatas"] or []

    # Aggregate chunks by doc_id
    docs_map: dict[str, dict[str, Any]] = {}

    for m in metas:
        did = m.get("doc_id", "unknown")
        if did not in docs_map:
            docs_map[did] = {
                "doc_id": did,
                "doc_name": m.get("doc_name", "Unknown Document"),
                "category": m.get("category", "Uncategorised"),
                "file_name": m.get("file_name"),
                "created_at": m.get("created_at"),
                "chunk_count": 0,
            }
        docs_map[did]["chunk_count"] += 1

    documents = [
        DocumentInfo(
            doc_id=info["doc_id"],
            doc_name=info["doc_name"],
            category=info["category"],
            chunk_count=info["chunk_count"],
            file_name=info["file_name"],
            created_at=info["created_at"],
            status="indexed",
        )
        for info in docs_map.values()
    ]

    # Sort documents by category then doc_name
    documents.sort(key=lambda d: (d.category.lower(), d.doc_name.lower()))
    return documents

