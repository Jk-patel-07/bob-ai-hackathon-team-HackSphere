"""
document_parser.py — Parse and chunk documents for ingestion.

Supported formats:
  - Markdown (.md, .txt)  — parsed directly; headings used as section labels
  - PDF (.pdf)            — text extracted with PyMuPDF (fitz)

Chunking strategy:
  RecursiveCharacterTextSplitter with a 512-token target chunk size and
  50-token overlap. Heading context is preserved in metadata so citations
  can reference the specific section of a document.

NOTE: The demo_data/ documents are clearly labelled as synthetic/educational.
      No real proprietary PDK, DRC, or semiconductor IP is included.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# Approximate token count for chunking (1 token ≈ 4 chars in English)
CHUNK_SIZE_CHARS = 2048   # ~512 tokens
CHUNK_OVERLAP_CHARS = 200  # ~50 tokens


@dataclass
class ParsedChunk:
    """A single text chunk with its associated metadata."""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _make_doc_id(file_path: str) -> str:
    """Derive a stable doc_id from the file path (SHA-256 prefix)."""
    return hashlib.sha256(os.path.abspath(file_path).encode()).hexdigest()[:16]


def _extract_markdown_sections(text: str) -> list[tuple[str | None, str]]:
    """Split Markdown text into (heading, body) pairs.

    Returns a list of (section_heading, text_block) tuples.  The first block
    may have heading=None if there is content before the first heading.
    """
    sections: list[tuple[str | None, str]] = []
    # Split on lines that start with one or more '#'
    pattern = re.compile(r"^(#{1,6}\s+.+)$", re.MULTILINE)
    parts = pattern.split(text)

    # parts alternates: [pre_heading_text, heading1, body1, heading2, body2, ...]
    if parts:
        pre = parts[0].strip()
        if pre:
            sections.append((None, pre))

    for i in range(1, len(parts), 2):
        heading = parts[i].lstrip("#").strip() if i < len(parts) else None
        body = parts[i + 1].strip() if (i + 1) < len(parts) else ""
        if body:
            sections.append((heading, body))

    return sections


def _parse_markdown(file_path: str) -> list[ParsedChunk]:
    """Parse a Markdown or plain-text file into chunks with section metadata."""
    path = Path(file_path)
    text = path.read_text(encoding="utf-8", errors="replace")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE_CHARS,
        chunk_overlap=CHUNK_OVERLAP_CHARS,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    sections = _extract_markdown_sections(text)
    chunks: list[ParsedChunk] = []

    for heading, body in sections:
        sub_chunks = splitter.split_text(body)
        for chunk_text in sub_chunks:
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue
            chunks.append(
                ParsedChunk(
                    text=chunk_text,
                    metadata={"section": heading, "page": None},
                )
            )

    logger.debug("Parsed %d chunks from %s (markdown)", len(chunks), file_path)
    return chunks


def _parse_pdf(file_path: str) -> list[ParsedChunk]:
    """Parse a PDF file into chunks with page number metadata."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise ImportError(
            "PyMuPDF is required for PDF parsing. "
            "Install it with: pip install pymupdf"
        ) from exc

    doc = fitz.open(file_path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE_CHARS,
        chunk_overlap=CHUNK_OVERLAP_CHARS,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[ParsedChunk] = []
    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text("text").strip()
        if not page_text:
            continue

        # Try to identify the first heading-like line on the page as section label
        first_line = page_text.split("\n")[0].strip()
        section_label = first_line if len(first_line) < 120 else None

        sub_chunks = splitter.split_text(page_text)
        for chunk_text in sub_chunks:
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue
            chunks.append(
                ParsedChunk(
                    text=chunk_text,
                    metadata={"section": section_label, "page": page_num},
                )
            )

    doc.close()
    logger.debug("Parsed %d chunks from %s (PDF, %d pages)", len(chunks), file_path, len(doc))
    return chunks


def parse_document(
    file_path: str,
    category: str,
    doc_name: str | None = None,
) -> tuple[str, str, list[ParsedChunk]]:
    """Parse a document file and return (doc_id, doc_name, chunks).

    Args:
        file_path: Path to the file to parse.
        category:  Knowledge category (e.g. 'PDK', 'DRC').
        doc_name:  Optional display name. Defaults to the filename stem.

    Returns:
        (doc_id, resolved_doc_name, list_of_ParsedChunks)

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError:        If the file format is not supported.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    resolved_name = doc_name or path.stem.replace("_", " ").replace("-", " ").title()
    doc_id = _make_doc_id(str(path))

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        raw_chunks = _parse_pdf(str(path))
    elif suffix in (".md", ".txt", ".rst"):
        raw_chunks = _parse_markdown(str(path))
    else:
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported: .pdf, .md, .txt, .rst"
        )

    created_at = datetime.now(timezone.utc).isoformat()

    # Enrich each chunk's metadata with document-level fields.
    for chunk in raw_chunks:
        chunk.metadata.update(
            {
                "doc_name": resolved_name,
                "category": category,
                "file_path": str(path.resolve()),
                "file_name": path.name,
                "created_at": created_at,
            }
        )

    logger.info(
        "Parsed document '%s' → %d chunks (category=%s, doc_id=%s)",
        resolved_name,
        len(raw_chunks),
        category,
        doc_id,
    )
    return doc_id, resolved_name, raw_chunks
