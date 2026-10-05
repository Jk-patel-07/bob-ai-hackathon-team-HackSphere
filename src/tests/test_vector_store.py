"""
test_vector_store.py — Unit tests for the vector store module.

Uses an isolated in-memory ChromaDB collection (via a temp directory)
so tests do not touch the real persisted knowledge base.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures — isolate ChromaDB per test
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_chroma(tmp_path, monkeypatch):
    """
    Redirect ChromaDB to a temp directory and reset the module-level cache
    so each test starts with a clean, empty collection.
    """
    import backend.vector_store as vs_module
    # Reset cached client and collection
    vs_module._chroma_client = None
    vs_module._collection = None
    # Point settings to temp dir
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_collection")
    # Invalidate settings cache so monkeypatch takes effect
    from backend.config import get_settings
    get_settings.cache_clear()
    yield
    # Cleanup
    vs_module._chroma_client = None
    vs_module._collection = None
    get_settings.cache_clear()


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def _dummy_embedding(dim: int = 8) -> list[float]:
    """Return a fake embedding vector of given dimension."""
    return [float(i) / dim for i in range(dim)]


def _make_embeddings(n: int, dim: int = 8) -> list[list[float]]:
    return [[float((i + j) % dim) / dim for j in range(dim)] for i in range(n)]


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestUpsertChunks:
    def test_upsert_returns_chunk_count(self):
        from backend.vector_store import upsert_chunks
        texts = ["chunk one", "chunk two", "chunk three"]
        embeddings = _make_embeddings(3)
        metas = [{"doc_name": "TestDoc", "category": "PDK"} for _ in texts]
        n = upsert_chunks(texts, embeddings, metas, doc_id="test123")
        assert n == 3

    def test_upsert_is_idempotent(self):
        from backend.vector_store import upsert_chunks, get_total_chunks
        texts = ["unique chunk"]
        embeddings = _make_embeddings(1)
        metas = [{"doc_name": "Doc", "category": "DRC"}]
        upsert_chunks(texts, embeddings, metas, doc_id="doc1")
        upsert_chunks(texts, embeddings, metas, doc_id="doc1")  # same doc_id
        assert get_total_chunks() == 1  # upsert, not insert

    def test_multiple_documents_stored_separately(self):
        from backend.vector_store import upsert_chunks, get_total_chunks
        for i in range(3):
            upsert_chunks(
                [f"chunk for doc {i}"],
                _make_embeddings(1),
                [{"doc_name": f"Doc{i}", "category": "PDK"}],
                doc_id=f"doc{i}",
            )
        assert get_total_chunks() == 3


class TestGetTotalChunks:
    def test_empty_collection_returns_zero(self):
        from backend.vector_store import get_total_chunks
        assert get_total_chunks() == 0

    def test_returns_correct_count_after_upsert(self):
        from backend.vector_store import upsert_chunks, get_total_chunks
        upsert_chunks(
            ["a", "b", "c", "d"],
            _make_embeddings(4),
            [{"category": "PDK"} for _ in range(4)],
            doc_id="d1",
        )
        assert get_total_chunks() == 4


class TestDeleteDocument:
    def test_delete_removes_all_chunks(self):
        from backend.vector_store import upsert_chunks, delete_document, get_total_chunks
        upsert_chunks(
            ["x", "y"],
            _make_embeddings(2),
            [{"category": "PDK"}, {"category": "PDK"}],
            doc_id="to_delete",
        )
        assert get_total_chunks() == 2
        n_deleted = delete_document("to_delete")
        assert n_deleted == 2
        assert get_total_chunks() == 0

    def test_delete_nonexistent_returns_zero(self):
        from backend.vector_store import delete_document
        assert delete_document("does_not_exist") == 0


class TestQueryChunks:
    def test_empty_collection_returns_empty(self):
        from backend.vector_store import query_chunks
        result = query_chunks(_dummy_embedding(), top_k=5)
        assert result == []

    def test_returns_at_most_top_k_chunks(self):
        from backend.vector_store import upsert_chunks, query_chunks
        texts = [f"text {i}" for i in range(10)]
        upsert_chunks(
            texts,
            _make_embeddings(10),
            [{"category": "DRC"} for _ in texts],
            doc_id="big_doc",
        )
        results = query_chunks(_dummy_embedding(), top_k=3)
        assert len(results) <= 3

    def test_results_have_required_keys(self):
        from backend.vector_store import upsert_chunks, query_chunks
        upsert_chunks(
            ["sample text"],
            _make_embeddings(1),
            [{"category": "PDK", "doc_name": "TestDoc"}],
            doc_id="doc_keys",
        )
        results = query_chunks(_dummy_embedding(), top_k=1)
        assert len(results) >= 1
        r = results[0]
        assert "text" in r
        assert "metadata" in r
        assert "similarity" in r

    def test_similarity_score_in_range(self):
        from backend.vector_store import upsert_chunks, query_chunks
        upsert_chunks(
            ["text one", "text two"],
            _make_embeddings(2),
            [{"category": "PDK"}, {"category": "PDK"}],
            doc_id="sim_test",
        )
        results = query_chunks(_dummy_embedding(), top_k=2)
        for r in results:
            assert 0.0 <= r["similarity"] <= 1.0

    def test_category_filter(self):
        from backend.vector_store import upsert_chunks, query_chunks
        upsert_chunks(
            ["PDK chunk"],
            _make_embeddings(1),
            [{"category": "PDK"}],
            doc_id="pdk_doc",
        )
        upsert_chunks(
            ["DRC chunk"],
            _make_embeddings(1),
            [{"category": "DRC"}],
            doc_id="drc_doc",
        )
        pdk_results = query_chunks(_dummy_embedding(), top_k=10, category="PDK")
        for r in pdk_results:
            assert r["metadata"]["category"] == "PDK"


class TestGetCategories:
    def test_empty_collection_returns_empty_list(self):
        from backend.vector_store import get_categories
        assert get_categories() == []

    def test_categories_aggregated_correctly(self):
        from backend.vector_store import upsert_chunks, get_categories
        upsert_chunks(
            ["pdk chunk 1", "pdk chunk 2"],
            _make_embeddings(2),
            [{"category": "PDK", "doc_id": "p1"}, {"category": "PDK", "doc_id": "p1"}],
            doc_id="p1",
        )
        upsert_chunks(
            ["drc chunk"],
            _make_embeddings(1),
            [{"category": "DRC", "doc_id": "d1"}],
            doc_id="d1",
        )
        cats = get_categories()
        names = [c.name for c in cats]
        assert "PDK" in names
        assert "DRC" in names

        pdk = next(c for c in cats if c.name == "PDK")
        assert pdk.chunk_count == 2
        assert pdk.doc_count == 1


class TestGetDocumentChunks:
    def test_returns_ordered_chunks(self):
        from backend.vector_store import upsert_chunks, get_document_chunks
        texts = ["first", "second", "third"]
        upsert_chunks(
            texts,
            _make_embeddings(3),
            [{"category": "PDK"} for _ in texts],
            doc_id="ordered_doc",
        )
        chunks = get_document_chunks("ordered_doc")
        assert len(chunks) == 3
        # chunk_index should be 0, 1, 2
        indices = [c["metadata"]["chunk_index"] for c in chunks]
        assert indices == sorted(indices)

    def test_unknown_doc_returns_empty(self):
        from backend.vector_store import get_document_chunks
        assert get_document_chunks("nonexistent") == []


class TestDocumentExists:
    def test_returns_false_for_unknown(self):
        from backend.vector_store import document_exists
        assert document_exists("unknown_id") is False

    def test_returns_true_after_upsert(self):
        from backend.vector_store import upsert_chunks, document_exists
        upsert_chunks(
            ["exists chunk"],
            _make_embeddings(1),
            [{"category": "PDK"}],
            doc_id="exists_id",
        )
        assert document_exists("exists_id") is True
