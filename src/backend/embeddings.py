"""
embeddings.py — Configurable embedding wrapper supporting Gemini and watsonx.ai.

Functions:
  embed_texts(texts) -> list[list[float]]
  embed_query(query) -> list[float]

The active provider is determined by settings.provider ('gemini' or 'watsonx').
If credentials for the selected provider are not configured, functions raise
a clear ConfigurationError.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .config import get_settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required AI provider credentials are missing."""


def _get_watsonx_embeddings_client():
    """Lazily create and return a watsonx.ai Embeddings client."""
    settings = get_settings()
    if not settings.watsonx_configured:
        raise ConfigurationError(
            "watsonx.ai credentials are not configured. "
            "Set WATSONX_API_KEY and WATSONX_PROJECT_ID in your .env file."
        )

    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import Embeddings
    from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams

    credentials = Credentials(
        url=settings.watsonx_url,
        api_key=settings.watsonx_api_key,
    )

    embed_params = {
        EmbedParams.TRUNCATE_INPUT_TOKENS: 512,
        EmbedParams.RETURN_OPTIONS: {"input_text": False},
    }

    client = Embeddings(
        model_id=settings.watsonx_embedding_model_id,
        credentials=credentials,
        project_id=settings.watsonx_project_id,
        params=embed_params,
    )
    return client


def _embed_texts_gemini(texts: list[str], settings) -> list[list[float]]:
    """Generate embeddings via Google Gemini API."""
    if not settings.gemini_configured:
        raise ConfigurationError(
            "Gemini API key is not configured. "
            "Set GEMINI_API_KEY in your .env file."
        )

    from google import genai
    client = genai.Client(api_key=settings.gemini_api_key)

    vectors: list[list[float]] = []
    try:
        response = client.models.embed_content(
            model=settings.gemini_embedding_model,
            contents=texts if len(texts) > 1 else texts[0],
        )
        if hasattr(response, "embeddings") and response.embeddings:
            for item in response.embeddings:
                vectors.append(list(item.values))
        elif hasattr(response, "embedding") and response.embedding:
            vectors.append(list(response.embedding.values))
        return vectors
    except Exception as exc:
        logger.error("Gemini embedding call failed: %s", exc)
        raise


def _embed_texts_watsonx(texts: list[str], settings) -> list[list[float]]:
    """Generate embeddings via IBM watsonx.ai SDK."""
    client = _get_watsonx_embeddings_client()
    try:
        response = client.embed_documents(texts=texts)
        vectors: list[list[float]] = []
        for item in response:
            if isinstance(item, dict):
                vectors.append(item["embedding"])
            else:
                vectors.append(list(item))
        return vectors
    except Exception as exc:
        logger.error("watsonx.ai embedding call failed: %s", exc)
        raise


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return embeddings for a list of text strings using the active AI provider.

    Args:
        texts: List of non-empty strings to embed.

    Returns:
        List of float vectors, one per input text.

    Raises:
        ConfigurationError: If active provider credentials are not set.
    """
    if not texts:
        return []

    settings = get_settings()
    provider = settings.provider
    logger.debug(
        "Embedding %d text(s) with provider '%s' (model: %s)",
        len(texts),
        provider,
        settings.active_embedding_model_id,
    )

    if provider == "gemini":
        return _embed_texts_gemini(texts, settings)
    else:
        return _embed_texts_watsonx(texts, settings)


def embed_query(query: str) -> list[float]:
    """Return a single embedding vector for a search query."""
    vectors = embed_texts([query])
    return vectors[0]
