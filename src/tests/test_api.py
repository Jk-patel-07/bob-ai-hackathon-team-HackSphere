"""
test_api.py — Integration tests for the FastAPI endpoints.

These tests start the FastAPI app with TestClient (no real server needed).
watsonx.ai calls are mocked — these tests verify API contract and routing,
not AI response quality.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def reset_chroma(tmp_path, monkeypatch):
    """Isolate each test with a fresh ChromaDB instance."""
    import backend.vector_store as vs_module
    vs_module._chroma_client = None
    vs_module._collection = None
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_api_col")
    # Also clear placeholder credentials so watsonx_configured=False by default
    monkeypatch.setenv("WATSONX_API_KEY", "your_watsonx_api_key_here")
    monkeypatch.setenv("WATSONX_PROJECT_ID", "")
    from backend.config import get_settings
    get_settings.cache_clear()
    yield
    vs_module._chroma_client = None
    vs_module._collection = None
    get_settings.cache_clear()


@pytest.fixture
def client(reset_chroma):
    """TestClient with NO watsonx credentials configured (default)."""
    from fastapi.testclient import TestClient
    from backend.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authed_client(tmp_path, monkeypatch):
    """TestClient with REAL-LOOKING watsonx credentials set before app starts."""
    import backend.vector_store as vs_module
    vs_module._chroma_client = None
    vs_module._collection = None
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma_authed"))
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_authed_col")
    monkeypatch.setenv("AI_PROVIDER", "watsonx")
    monkeypatch.setenv("WATSONX_API_KEY", "real_looking_key_abc123")
    monkeypatch.setenv("WATSONX_PROJECT_ID", "real_proj_id_xyz")
    from backend.config import get_settings
    get_settings.cache_clear()
    from fastapi.testclient import TestClient
    from backend.main import app
    with TestClient(app) as c:
        yield c
    vs_module._chroma_client = None
    vs_module._collection = None
    get_settings.cache_clear()


# ─────────────────────────────────────────────────────────────────────────────
# Health endpoint
# ─────────────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_schema(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert "status" in data
        assert "vector_store" in data
        assert "ai_provider" in data
        assert "provider_configured" in data
        assert "watsonx_configured" in data
        assert "llm_model" in data
        assert "embedding_model" in data
        assert "total_chunks" in data

    def test_health_status_ok(self, client):
        resp = client.get("/health")
        assert resp.json()["status"] == "ok"

    def test_health_total_chunks_zero_initially(self, client):
        resp = client.get("/health")
        assert resp.json()["total_chunks"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# Categories endpoint
# ─────────────────────────────────────────────────────────────────────────────

class TestCategories:
    def test_categories_empty_on_fresh_db(self, client):
        resp = client.get("/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert data["categories"] == []
        assert data["total_documents"] == 0
        assert data["total_chunks"] == 0

    def test_categories_schema(self, client):
        resp = client.get("/categories")
        data = resp.json()
        assert "categories" in data
        assert "total_documents" in data
        assert "total_chunks" in data


# ─────────────────────────────────────────────────────────────────────────────
# Ingest endpoint (with mocked watsonx.ai)
# ─────────────────────────────────────────────────────────────────────────────

class TestIngest:
    def test_ingest_nonexistent_file_returns_404(self, authed_client):
        resp = authed_client.post("/ingest", json={
            "file_path": "/does/not/exist/file.md",
            "category": "PDK",
        })
        assert resp.status_code == 404

    def test_ingest_unsupported_format_returns_400(self, authed_client, tmp_path):
        bad_file = tmp_path / "data.xyz"
        bad_file.write_text("content")
        resp = authed_client.post("/ingest", json={
            "file_path": str(bad_file),
            "category": "PDK",
        })
        assert resp.status_code == 400

    def test_ingest_without_credentials_returns_503(self, client, tmp_path):
        """client fixture has NO credentials — 503 expected after file validation."""
        md = tmp_path / "test.md"
        md.write_text("# Test\n\nContent.")
        resp = client.post("/ingest", json={
            "file_path": str(md),
            "category": "PDK",
        })
        assert resp.status_code == 503

    def test_ingest_with_mocked_embeddings(self, authed_client, tmp_path):
        """Verify full ingest pipeline works when embeddings are mocked."""
        md = tmp_path / "rules.md"
        md.write_text(
            "# Gate Width Rule\n\nMinimum gate width is 200 nm.\n\n"
            "# Spacing Rule\n\nMinimum metal spacing is 200 nm.\n"
        )

        with patch("backend.main.embed_texts") as mock_embed:
            mock_embed.side_effect = lambda texts: [[0.1] * 8 for _ in texts]
            resp = authed_client.post("/ingest", json={
                "file_path": str(md),
                "category": "PDK",
                "doc_name": "Test PDK Rules",
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["doc_name"] == "Test PDK Rules"
        assert data["category"] == "PDK"
        assert data["chunks_created"] >= 1
        assert data["status"] == "ok"
        assert len(data["doc_id"]) == 16


# ─────────────────────────────────────────────────────────────────────────────
# Search endpoint (with mocked watsonx.ai)
# ─────────────────────────────────────────────────────────────────────────────

class TestSearch:
    def test_search_empty_db_returns_insufficient(self, authed_client):
        with patch("backend.rag_engine.embed_query") as mock_embed:
            mock_embed.return_value = [0.1] * 8
            resp = authed_client.post("/search", json={"query": "minimum gate length"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["sufficient_context"] is False
        assert data["retrieved_chunks"] == 0
        assert "insufficient" in data["answer"].lower() or "not contain" in data["answer"].lower()

    def test_search_schema(self, authed_client):
        with patch("backend.rag_engine.embed_query") as mock_embed:
            mock_embed.return_value = [0.1] * 8
            resp = authed_client.post("/search", json={"query": "what is the minimum width"})

        assert resp.status_code == 200
        data = resp.json()
        assert "query" in data
        assert "answer" in data
        assert "citations" in data
        assert "retrieved_chunks" in data
        assert "sufficient_context" in data
        assert "model_used" in data

    def test_search_with_results_calls_llm(self, authed_client, tmp_path):
        """Verify that when chunks exist, the LLM is called for generation."""
        md = tmp_path / "pdk.md"
        md.write_text("# Minimum Gate Width\n\nThe minimum gate width is 200 nm.")

        with patch("backend.main.embed_texts") as mock_embed_texts:
            mock_embed_texts.side_effect = lambda texts: [[0.5] * 8 for _ in texts]
            authed_client.post("/ingest", json={
                "file_path": str(md),
                "category": "PDK",
                "doc_name": "Test PDK",
            })

        with patch("backend.rag_engine.embed_query") as mock_embed_q, \
             patch("backend.rag_engine._get_llm_client") as mock_llm:
            mock_embed_q.return_value = [0.5] * 8
            mock_llm_instance = MagicMock()
            mock_llm_instance.generate_text.return_value = (
                "The minimum gate width is 200 nm as per the PDK design rules."
            )
            mock_llm.return_value = mock_llm_instance

            resp = authed_client.post("/search", json={"query": "minimum gate width"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["sufficient_context"] is True
        assert "200 nm" in data["answer"]
        assert len(data["citations"]) >= 1

    def test_search_missing_query_returns_422(self, client):
        resp = client.post("/search", json={})
        assert resp.status_code == 422

    def test_search_short_query_returns_422(self, client):
        resp = client.post("/search", json={"query": "ab"})
        assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# Document sections endpoint
# ─────────────────────────────────────────────────────────────────────────────

class TestDocumentSections:
    def test_unknown_doc_id_returns_404(self, client):
        resp = client.get("/documents/nonexistent_id/sections")
        assert resp.status_code == 404

    def test_known_doc_id_returns_sections(self, authed_client, tmp_path):
        md = tmp_path / "doc.md"
        md.write_text("# Section A\n\nContent A.\n\n# Section B\n\nContent B.")

        with patch("backend.main.embed_texts") as mock_embed:
            mock_embed.side_effect = lambda texts: [[0.1] * 8 for _ in texts]
            resp = authed_client.post("/ingest", json={
                "file_path": str(md),
                "category": "PDK",
                "doc_name": "Two-Section Doc",
            })

        doc_id = resp.json()["doc_id"]
        sections_resp = authed_client.get(f"/documents/{doc_id}/sections")
        assert sections_resp.status_code == 200
        data = sections_resp.json()
        assert data["doc_id"] == doc_id
        assert data["doc_name"] == "Two-Section Doc"
        assert len(data["sections"]) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Document Listing, Upload, and Delete
# ─────────────────────────────────────────────────────────────────────────────

class TestDocumentList:
    def test_list_documents_empty(self, client):
        resp = client.get("/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert data["documents"] == []
        assert data["total_documents"] == 0

    def test_list_documents_after_ingest(self, authed_client, tmp_path):
        md = tmp_path / "rules.md"
        md.write_text("# DRC Rules\n\nRule 1: Spacing must be >= 100nm.")

        with patch("backend.main.embed_texts") as mock_embed:
            mock_embed.side_effect = lambda texts: [[0.1] * 8 for _ in texts]
            authed_client.post("/ingest", json={
                "file_path": str(md),
                "category": "DRC",
                "doc_name": "DRC Spec",
            })

        resp = authed_client.get("/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_documents"] == 1
        doc = data["documents"][0]
        assert doc["doc_name"] == "DRC Spec"
        assert doc["category"] == "DRC"
        assert doc["chunk_count"] == 1


class TestDocumentUpload:
    def test_upload_without_credentials_returns_503(self, client):
        resp = client.post(
            "/documents/upload",
            data={"category": "PDK"},
            files={"file": ("test.md", b"# Header\nContent", "text/markdown")},
        )
        assert resp.status_code == 503

    def test_upload_unsupported_format_returns_400(self, authed_client):
        resp = authed_client.post(
            "/documents/upload",
            data={"category": "PDK"},
            files={"file": ("test.exe", b"binary content", "application/octet-stream")},
        )
        assert resp.status_code == 400
        assert "Unsupported file extension" in resp.json()["detail"]

    def test_upload_empty_file_returns_400(self, authed_client):
        resp = authed_client.post(
            "/documents/upload",
            data={"category": "PDK"},
            files={"file": ("empty.md", b"", "text/markdown")},
        )
        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"]

    def test_upload_success_with_mocked_embeddings(self, authed_client):
        with patch("backend.main.embed_texts") as mock_embed:
            mock_embed.side_effect = lambda texts: [[0.2] * 8 for _ in texts]
            resp = authed_client.post(
                "/documents/upload",
                data={"category": "Design Guidelines", "doc_name": "Custom Upload Doc"},
                files={"file": ("guide.md", b"# Latchup\nAvoid parasitic SCR.", "text/markdown")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["doc_name"] == "Custom Upload Doc"
        assert data["category"] == "Design Guidelines"
        assert data["chunks_created"] == 1

    def test_upload_duplicate_returns_409(self, authed_client):
        file_bytes = b"# Duplicate Test\nExact same content."
        with patch("backend.main.embed_texts") as mock_embed:
            mock_embed.side_effect = lambda texts: [[0.3] * 8 for _ in texts]
            resp1 = authed_client.post(
                "/documents/upload",
                data={"category": "SPICE Models"},
                files={"file": ("model.md", file_bytes, "text/markdown")},
            )
            assert resp1.status_code == 200

            resp2 = authed_client.post(
                "/documents/upload",
                data={"category": "SPICE Models"},
                files={"file": ("model_copy.md", file_bytes, "text/markdown")},
            )
            assert resp2.status_code == 409
            assert "already exists" in resp2.json()["detail"]


class TestDocumentDelete:
    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete("/documents/nonexistent_doc_123")
        assert resp.status_code == 404

    def test_delete_existing_document(self, authed_client, tmp_path):
        md = tmp_path / "to_delete.md"
        md.write_text("# Temporary Doc\nWill be deleted.")

        with patch("backend.main.embed_texts") as mock_embed:
            mock_embed.side_effect = lambda texts: [[0.1] * 8 for _ in texts]
            ingest_resp = authed_client.post("/ingest", json={
                "file_path": str(md),
                "category": "PDK",
                "doc_name": "Delete Me",
            })

        doc_id = ingest_resp.json()["doc_id"]

        del_resp = authed_client.delete(f"/documents/{doc_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["chunks_deleted"] == 1

        list_resp = authed_client.get("/documents")
        assert list_resp.json()["total_documents"] == 0

