"""
config.py — centralised settings loaded from environment variables.

All configuration is read from environment variables (or a .env file).
Nothing is hardcoded; model IDs, credentials, and tuning knobs are all
overridable at runtime.
"""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Values are read from environment variables first, then from a .env file
    in the working directory (src/.env), then from src/.env.example defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── AI Provider Selection ──────────────────────────────────────────────
    ai_provider: str = "gemini"  # "gemini" or "watsonx"

    # ── Google Gemini credentials & models ─────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-001"

    # ── watsonx.ai credentials & models ────────────────────────────────────
    watsonx_api_key: str = ""
    watsonx_project_id: str = ""
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_llm_model_id: str = "ibm/granite-13b-instruct-v2"
    watsonx_embedding_model_id: str = "ibm/slate-125m-english-rtrvr"

    # ── Application ────────────────────────────────────────────────────────
    app_port: int = 8000
    app_env: str = "development"
    log_level: str = "INFO"

    # ── ChromaDB ───────────────────────────────────────────────────────────
    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "chip_design_knowledge"

    # ── MCP → Backend ──────────────────────────────────────────────────────
    backend_url: str = "http://localhost:8000"

    # ── RAG tuning ─────────────────────────────────────────────────────────
    rag_top_k: int = 5
    rag_min_similarity: float = 0.30

    @property
    def provider(self) -> str:
        """Return active provider name ('gemini' or 'watsonx')."""
        prov = self.ai_provider.strip().lower() if self.ai_provider else "gemini"
        return "watsonx" if prov == "watsonx" else "gemini"

    @property
    def gemini_configured(self) -> bool:
        """Return True when required Gemini API key is present."""
        return bool(
            self.gemini_api_key
            and self.gemini_api_key != "your_gemini_api_key_here"
        )

    @property
    def watsonx_configured(self) -> bool:
        """Return True only when all required watsonx credentials are present."""
        return bool(
            self.watsonx_api_key
            and self.watsonx_api_key != "your_watsonx_api_key_here"
            and self.watsonx_project_id
            and self.watsonx_project_id != "your_watsonx_project_id_here"
        )

    @property
    def provider_configured(self) -> bool:
        """Return True if active AI provider credentials are valid."""
        if self.provider == "gemini":
            return self.gemini_configured
        elif self.provider == "watsonx":
            return self.watsonx_configured
        return False

    @property
    def active_llm_model_id(self) -> str:
        """Return LLM model ID for the active provider."""
        if self.provider == "gemini":
            return self.gemini_model
        return self.watsonx_llm_model_id

    @property
    def active_embedding_model_id(self) -> str:
        """Return embedding model ID for the active provider."""
        if self.provider == "gemini":
            return self.gemini_embedding_model
        return self.watsonx_embedding_model_id


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()
