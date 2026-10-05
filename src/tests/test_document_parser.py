"""
test_document_parser.py — Unit tests for the document parser module.

These tests run without watsonx.ai credentials or a running backend.
They only test local file parsing logic.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

# Add src/ to path so tests can import backend package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.document_parser import (
    ParsedChunk,
    _extract_markdown_sections,
    _make_doc_id,
    _parse_markdown,
    parse_document,
)


# ─────────────────────────────────────────────────────────────────────────────
# _make_doc_id
# ─────────────────────────────────────────────────────────────────────────────

class TestMakeDocId:
    def test_returns_16_char_hex(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("hello")
        doc_id = _make_doc_id(str(p))
        assert len(doc_id) == 16
        assert all(c in "0123456789abcdef" for c in doc_id)

    def test_stable_for_same_path(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("hello")
        assert _make_doc_id(str(p)) == _make_doc_id(str(p))

    def test_different_for_different_paths(self, tmp_path):
        p1 = tmp_path / "a.md"
        p2 = tmp_path / "b.md"
        p1.write_text("x")
        p2.write_text("x")
        assert _make_doc_id(str(p1)) != _make_doc_id(str(p2))


# ─────────────────────────────────────────────────────────────────────────────
# _extract_markdown_sections
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractMarkdownSections:
    def test_single_heading(self):
        text = "# Introduction\n\nSome content here."
        sections = _extract_markdown_sections(text)
        assert len(sections) == 1
        heading, body = sections[0]
        assert heading == "Introduction"
        assert "content" in body

    def test_multiple_headings(self):
        text = "# Section A\n\nBody A.\n\n## Section B\n\nBody B."
        sections = _extract_markdown_sections(text)
        assert len(sections) == 2
        assert sections[0][0] == "Section A"
        assert sections[1][0] == "Section B"

    def test_content_before_first_heading(self):
        text = "Preamble text.\n\n# Heading\n\nBody."
        sections = _extract_markdown_sections(text)
        # First section has no heading (None)
        assert sections[0][0] is None
        assert "Preamble" in sections[0][1]

    def test_empty_text(self):
        sections = _extract_markdown_sections("")
        assert sections == []

    def test_no_headings(self):
        text = "Just plain text.\nNo headings here."
        sections = _extract_markdown_sections(text)
        assert len(sections) == 1
        assert sections[0][0] is None


# ─────────────────────────────────────────────────────────────────────────────
# _parse_markdown
# ─────────────────────────────────────────────────────────────────────────────

class TestParseMarkdown:
    def test_basic_markdown_produces_chunks(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            "# Rule 1\n\nThe minimum gate length is 130 nm.\n\n"
            "# Rule 2\n\nThe minimum metal width is 200 nm.\n"
        )
        chunks = _parse_markdown(str(md))
        assert len(chunks) >= 2
        assert all(isinstance(c, ParsedChunk) for c in chunks)

    def test_section_metadata_populated(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# My Section\n\nContent of the section.")
        chunks = _parse_markdown(str(md))
        assert len(chunks) >= 1
        assert chunks[0].metadata["section"] == "My Section"

    def test_page_metadata_is_none_for_markdown(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Heading\n\nSome text.")
        chunks = _parse_markdown(str(md))
        for chunk in chunks:
            assert chunk.metadata["page"] is None

    def test_long_document_produces_multiple_chunks(self, tmp_path):
        md = tmp_path / "long.md"
        # Write a document large enough to require chunking
        content = "# Long Section\n\n" + ("This is a sentence about chip design rules. " * 200)
        md.write_text(content)
        chunks = _parse_markdown(str(md))
        assert len(chunks) >= 2


# ─────────────────────────────────────────────────────────────────────────────
# parse_document (integration)
# ─────────────────────────────────────────────────────────────────────────────

class TestParseDocument:
    def test_returns_doc_id_name_and_chunks(self, tmp_path):
        md = tmp_path / "my_rules.md"
        md.write_text("# Gate Rules\n\nMinimum gate length is 130 nm.\n")
        doc_id, doc_name, chunks = parse_document(str(md), category="PDK")
        assert isinstance(doc_id, str) and len(doc_id) == 16
        assert "My Rules" in doc_name  # title-cased from filename
        assert len(chunks) >= 1

    def test_custom_doc_name(self, tmp_path):
        md = tmp_path / "file.md"
        md.write_text("# Section\n\nContent.")
        _, doc_name, _ = parse_document(str(md), category="DRC", doc_name="Custom Name")
        assert doc_name == "Custom Name"

    def test_metadata_includes_category_and_doc_name(self, tmp_path):
        md = tmp_path / "rules.md"
        md.write_text("# PDK Rules\n\nMinimum width is 200 nm.")
        _, _, chunks = parse_document(str(md), category="PDK", doc_name="Test PDK")
        for chunk in chunks:
            assert chunk.metadata["category"] == "PDK"
            assert chunk.metadata["doc_name"] == "Test PDK"

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_document("/nonexistent/path/file.md", category="PDK")

    def test_unsupported_format(self, tmp_path):
        f = tmp_path / "data.xyz"
        f.write_text("some content")
        with pytest.raises(ValueError, match="Unsupported file format"):
            parse_document(str(f), category="PDK")

    def test_txt_file_supported(self, tmp_path):
        f = tmp_path / "notes.txt"
        f.write_text("Design notes.\nUse minimum width of 200 nm.")
        doc_id, _, chunks = parse_document(str(f), category="Design Guidelines")
        assert len(chunks) >= 1

    def test_demo_data_parseable(self):
        """Verify all demo_data documents parse without errors."""
        demo_dir = Path(__file__).parent.parent / "demo_data"
        for md_file in demo_dir.glob("*.md"):
            if md_file.name == "README.md":
                continue
            doc_id, doc_name, chunks = parse_document(
                str(md_file), category="Demo"
            )
            assert len(chunks) >= 1, f"{md_file.name} produced no chunks"
            for chunk in chunks:
                assert chunk.text.strip(), f"Empty chunk in {md_file.name}"
