"""
seed_demo_data.py — Ingest all synthetic demo documents into the knowledge base.

Run this script once after starting the backend to populate the knowledge base
with the five synthetic chip design documents included in demo_data/.

Usage:
    cd src
    python scripts/seed_demo_data.py

Requirements:
    - The FastAPI backend must be running: uvicorn backend.main:app --reload
    - watsonx.ai credentials must be set in src/.env
    - All dependencies installed: pip install -r requirements.txt

What this does:
    Calls the /ingest endpoint for each document in demo_data/.
    Each document is chunked, embedded via watsonx.ai, and stored in ChromaDB.
    Re-running the script is safe — it upserts (replaces existing chunks).

After running:
    Check the knowledge base: curl http://localhost:8000/categories
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

# ─────────────────────────────────────────────────────────────────────────────
# Document manifest — one entry per file
# ─────────────────────────────────────────────────────────────────────────────

# Paths are relative to the src/ directory (the working directory for this script)
DEMO_DOCUMENTS = [
    {
        "file_path": "demo_data/synthetic_pdk_design_rules.md",
        "category": "PDK",
        "doc_name": "Synthetic PDK Design Rules — ST130 Educational Process",
    },
    {
        "file_path": "demo_data/synthetic_drc_standard_cells.md",
        "category": "DRC",
        "doc_name": "Synthetic DRC Rule Deck — ST130 Standard Cells",
    },
    {
        "file_path": "demo_data/synthetic_latchup_guidelines.md",
        "category": "Design Guidelines",
        "doc_name": "Synthetic Latch-Up Prevention Guidelines — ST130",
    },
    {
        "file_path": "demo_data/synthetic_spice_model_notes.md",
        "category": "SPICE Models",
        "doc_name": "Synthetic SPICE Model Usage Notes — ST130",
    },
    {
        "file_path": "demo_data/synthetic_timing_constraints.md",
        "category": "Application Notes",
        "doc_name": "Synthetic Static Timing Analysis Guide — ST130",
    },
]


def ingest_document(
    client: httpx.Client,
    backend_url: str,
    doc: dict,
    verbose: bool = True,
) -> bool:
    """POST /ingest for a single document. Returns True on success."""
    url = f"{backend_url}/ingest"
    if verbose:
        print(f"\n  Ingesting: {doc['file_path']}")
        print(f"  Category:  {doc['category']}")

    # Resolve the file path relative to the src/ directory.
    src_dir = Path(__file__).parent.parent  # scripts/ -> src/
    abs_path = str((src_dir / doc["file_path"]).resolve())

    payload = {
        "file_path": abs_path,
        "category": doc["category"],
        "doc_name": doc["doc_name"],
    }

    try:
        response = client.post(url, json=payload, timeout=120.0)
        if response.status_code == 200:
            result = response.json()
            if verbose:
                print(f"  ✅  {result['doc_name']}")
                print(f"      Chunks stored: {result['chunks_created']}")
                print(f"      Doc ID:        {result['doc_id']}")
            return True
        else:
            detail = ""
            try:
                detail = response.json().get("detail", response.text[:200])
            except Exception:
                detail = response.text[:200]
            print(f"  ❌  HTTP {response.status_code}: {detail}")
            return False
    except httpx.ConnectError:
        print(f"\n❌ Cannot reach backend at {backend_url}")
        print("   Please start the backend first:")
        print("   cd src && uvicorn backend.main:app --reload\n")
        return False
    except Exception as exc:
        print(f"  ❌  Unexpected error: {exc}")
        return False


def check_backend(client: httpx.Client, backend_url: str) -> bool:
    """Return True if the backend is reachable and healthy."""
    try:
        resp = client.get(f"{backend_url}/health", timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            if not data.get("watsonx_configured"):
                print("\n⚠️  WARNING: watsonx.ai credentials are not configured.")
                print("   Ingestion will fail because embeddings cannot be generated.")
                print("   Set WATSONX_API_KEY and WATSONX_PROJECT_ID in src/.env\n")
                return False
            return True
        return False
    except httpx.ConnectError:
        return False


def print_summary(client: httpx.Client, backend_url: str) -> None:
    """Print the knowledge base contents after ingestion."""
    try:
        resp = client.get(f"{backend_url}/categories", timeout=10.0)
        if resp.status_code == 200:
            data = resp.json()
            cats = data.get("categories", [])
            total_docs = data.get("total_documents", 0)
            total_chunks = data.get("total_chunks", 0)
            print(f"\n{'─'*60}")
            print(f"Knowledge Base Summary")
            print(f"{'─'*60}")
            print(f"Total documents : {total_docs}")
            print(f"Total chunks    : {total_chunks}")
            if cats:
                print(f"\n{'Category':<25} {'Docs':>6} {'Chunks':>8}")
                print(f"{'─'*25} {'─'*6} {'─'*8}")
                for cat in cats:
                    print(f"{cat['name']:<25} {cat['doc_count']:>6} {cat['chunk_count']:>8}")
    except Exception as exc:
        print(f"Could not retrieve summary: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed the chip design knowledge base with demo documents."
    )
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="Base URL of the FastAPI backend (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-chunk progress output",
    )
    args = parser.parse_args()

    backend_url = args.backend_url.rstrip("/")
    verbose = not args.quiet

    print("=" * 60)
    print("Chip Design Knowledge Assistant — Demo Data Seeder")
    print("=" * 60)
    print(f"\nBackend URL: {backend_url}")
    print(f"Documents  : {len(DEMO_DOCUMENTS)}")
    print("\nChecking backend health…")

    with httpx.Client() as client:
        if not check_backend(client, backend_url):
            print(f"\n❌ Backend not reachable or not ready at {backend_url}")
            print("   Start the backend with: cd src && uvicorn backend.main:app --reload")
            return 1

        print("✅ Backend is healthy and watsonx.ai is configured.\n")
        print(f"Starting ingestion of {len(DEMO_DOCUMENTS)} documents…")
        print("(This may take 1–3 minutes per document due to embedding API calls)\n")

        successes = 0
        failures = 0
        start_time = time.time()

        for i, doc in enumerate(DEMO_DOCUMENTS, start=1):
            print(f"[{i}/{len(DEMO_DOCUMENTS)}]", end="")
            ok = ingest_document(client, backend_url, doc, verbose=verbose)
            if ok:
                successes += 1
            else:
                failures += 1

        elapsed = time.time() - start_time
        print(f"\n{'─'*60}")
        print(f"Ingestion complete in {elapsed:.1f}s")
        print(f"  ✅ Succeeded: {successes}")
        if failures:
            print(f"  ❌ Failed:    {failures}")

        print_summary(client, backend_url)

    if failures > 0:
        print(f"\n⚠️  {failures} document(s) failed to ingest. Check the output above for details.")
        return 1

    print(f"\n🎉 All {successes} documents ingested successfully!")
    print("   You can now query the knowledge base via:")
    print("   - IBM Bob IDE (chip-design-assistant mode + MCP)")
    print("   - API: POST http://localhost:8000/search")
    print("   - API docs: http://localhost:8000/docs\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
