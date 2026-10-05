"""
test_config.py — Unit tests for the configuration/settings module.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSettings:
    def test_watsonx_not_configured_with_placeholder_key(self, monkeypatch):
        from backend.config import get_settings, Settings
        get_settings.cache_clear()
        monkeypatch.setenv("WATSONX_API_KEY", "your_watsonx_api_key_here")
        monkeypatch.setenv("WATSONX_PROJECT_ID", "some_project")
        s = Settings()
        assert s.watsonx_configured is False
        get_settings.cache_clear()

    def test_watsonx_not_configured_with_empty_key(self, monkeypatch):
        from backend.config import Settings
        monkeypatch.setenv("WATSONX_API_KEY", "")
        monkeypatch.setenv("WATSONX_PROJECT_ID", "some_project")
        s = Settings()
        assert s.watsonx_configured is False

    def test_watsonx_configured_with_real_looking_key(self, monkeypatch):
        from backend.config import Settings
        monkeypatch.setenv("WATSONX_API_KEY", "abc123_real_key_value")
        monkeypatch.setenv("WATSONX_PROJECT_ID", "proj-12345")
        s = Settings()
        assert s.watsonx_configured is True

    def test_gemini_not_configured_with_placeholder_key(self, monkeypatch):
        from backend.config import Settings
        monkeypatch.setenv("GEMINI_API_KEY", "your_gemini_api_key_here")
        s = Settings()
        assert s.gemini_configured is False

    def test_gemini_configured_with_real_looking_key(self, monkeypatch):
        from backend.config import Settings
        monkeypatch.setenv("GEMINI_API_KEY", "AIzaSy_fake_test_key_12345")
        s = Settings()
        assert s.gemini_configured is True

    def test_provider_selection_gemini(self, monkeypatch):
        from backend.config import Settings
        monkeypatch.setenv("AI_PROVIDER", "gemini")
        monkeypatch.setenv("GEMINI_API_KEY", "AIzaSy_test_key")
        s = Settings()
        assert s.provider == "gemini"
        assert s.provider_configured is True
        assert s.active_llm_model_id == s.gemini_model

    def test_provider_selection_watsonx(self, monkeypatch):
        from backend.config import Settings
        monkeypatch.setenv("AI_PROVIDER", "watsonx")
        monkeypatch.setenv("WATSONX_API_KEY", "real_key")
        monkeypatch.setenv("WATSONX_PROJECT_ID", "real_proj")
        s = Settings()
        assert s.provider == "watsonx"
        assert s.provider_configured is True
        assert s.active_llm_model_id == s.watsonx_llm_model_id

    def test_default_model_ids(self):
        from backend.config import Settings
        s = Settings()
        assert "granite" in s.watsonx_llm_model_id.lower()
        assert "slate" in s.watsonx_embedding_model_id.lower()
        assert "gemini" in s.gemini_model.lower()
        assert "gemini" in s.gemini_embedding_model.lower()

    def test_default_rag_top_k(self):
        from backend.config import Settings
        s = Settings()
        assert s.rag_top_k == 5

    def test_default_min_similarity(self):
        from backend.config import Settings
        s = Settings()
        assert 0.0 < s.rag_min_similarity < 1.0

    def test_model_id_overridable(self, monkeypatch):
        from backend.config import Settings
        monkeypatch.setenv("WATSONX_LLM_MODEL_ID", "meta-llama/llama-3-70b-instruct")
        s = Settings()
        assert s.watsonx_llm_model_id == "meta-llama/llama-3-70b-instruct"

    def test_backend_url_default(self):
        from backend.config import Settings
        s = Settings()
        assert s.backend_url == "http://localhost:8000"

    def teardown_method(self):
        from backend.config import get_settings
        get_settings.cache_clear()
