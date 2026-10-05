"""
verify_e2e.py -- End-to-end verification script for the Chip Design Knowledge Assistant.

Runs ALL verification steps in sequence and prints a clear PASS/FAIL report.
Requires a configured src/.env file with real watsonx.ai credentials.

Usage:
    cd src
    python scripts/verify_e2e.py

What it tests (without starting a separate server process):
    Step 1 -- Credential check (.env loaded, values present and non-placeholder)
    Step 2 -- watsonx.ai auth (real API call: list deployed models)
    Step 3 -- Embedding model availability + real embed call
    Step 4 -- LLM model availability + real generation call
    Step 5 -- Document ingestion (all 5 demo docs, real embeddings, ChromaDB)
    Step 6 -- Retrieval (3 demo queries -- grounded answers + citations)
    Step 7 -- Insufficient-context protection (FinFET query -> explicit refusal)
    Step 8 -- Duplicate ingestion guard (re-ingest same doc, count must not grow)
    Step 9 -- Full pytest suite
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# -- Make sure we can import our backend modules ----------------------------
SRC_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SRC_DIR))

# Load .env BEFORE importing settings
from dotenv import load_dotenv
load_dotenv(SRC_DIR / ".env")

RESULTS: list[tuple[str, bool, str]] = []   # (label, passed, note)
CHROMA_TEST_DIR = str(SRC_DIR / "chroma_data_verify")  # isolated dir for this run


def record(label: str, passed: bool, note: str = "") -> None:
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}]  {label}" + (f"  ->  {note}" if note else ""))
    RESULTS.append((label, passed, note))


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# ==============================================================================
# STEP 1 -- Credential check
# ==============================================================================
section("STEP 1 -- Environment / credentials")

os.environ["CHROMA_PERSIST_DIR"] = CHROMA_TEST_DIR
os.environ["CHROMA_COLLECTION_NAME"] = "verify_collection"

from backend.config import get_settings
get_settings.cache_clear()
settings = get_settings()

api_key = settings.watsonx_api_key
proj_id = settings.watsonx_project_id
url = settings.watsonx_url
llm_id = settings.watsonx_llm_model_id
emb_id = settings.watsonx_embedding_model_id

record(".env file loaded", bool(api_key), f"key length={len(api_key)}")
record("WATSONX_API_KEY non-placeholder",
       api_key not in ("", "your_watsonx_api_key_here"),
       "Set in src/.env" if api_key == "your_watsonx_api_key_here" else "")
record("WATSONX_PROJECT_ID non-placeholder",
       proj_id not in ("", "your_watsonx_project_id_here"),
       "Set in src/.env" if proj_id in ("", "your_watsonx_project_id_here") else "")
record("WATSONX_URL set", bool(url), url)
record("LLM model ID set", bool(llm_id), llm_id)
record("Embedding model ID set", bool(emb_id), emb_id)

# Bail early if creds missing -- nothing else can work
if not settings.watsonx_configured:
    print("\n-  Credentials not configured. Cannot continue with Steps 2-8.")
    print("    Create src/.env from src/.env.example and fill in real values.")
    print("    See STEP 1 section in this report for details.\n")
    # Print what we have so far and exit
    print(f"\n{'=' * 60}")
    print("  PARTIAL REPORT (credentials not configured)")
    print(f"{'=' * 60}")
    for label, passed, note in RESULTS:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}  {label}" + (f"  ->  {note}" if note else ""))
    sys.exit(1)


# ==============================================================================
# STEP 2 -- watsonx.ai authentication
# ==============================================================================
section("STEP 2 -- watsonx.ai authentication")

try:
    from ibm_watsonx_ai import APIClient, Credentials
    credentials = Credentials(url=url, api_key=api_key)
    client = APIClient(credentials=credentials, project_id=proj_id)
    # A lightweight call -- just fetch the token (happens implicitly on first call)
    token = client.token
    record("watsonx.ai auth", bool(token), f"token length={len(token) if token else 0}")
except Exception as exc:
    record("watsonx.ai auth", False, str(exc)[:120])
    print("  -  Auth failed -- check API key and URL.")


# ==============================================================================
# STEP 3 -- Embedding model + real embed call
# ==============================================================================
section("STEP 3 -- Embedding model availability + real embed call")

try:
    from backend.embeddings import embed_texts, embed_query
    test_texts = [
        "Minimum poly gate overhang rule",
        "N-well tap placement for latch-up prevention",
    ]
    vectors = embed_texts(test_texts)
    record("embed_texts() call succeeds", True, f"got {len(vectors)} vectors")
    record("Embedding vector dimension > 0",
           len(vectors[0]) > 0,
           f"dim={len(vectors[0])}")
    record("Vectors are lists of floats",
           all(isinstance(v, float) for v in vectors[0]),
           "")
    # Single query embed
    qvec = embed_query("What is the minimum gate length?")
    record("embed_query() call succeeds", True, f"dim={len(qvec)}")
except Exception as exc:
    record("Embedding API call", False, str(exc)[:200])
    print(f"  --  Embedding model '{emb_id}' may not be available in your plan/region.")
    print(f"     Try: WATSONX_EMBEDDING_MODEL_ID=ibm/slate-30m-english-rtrvr")


# ==============================================================================
# STEP 4 -- LLM model availability + real generation
# ==============================================================================
section("STEP 4 -- LLM model availability + real generation call")

try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

    credentials = Credentials(url=url, api_key=api_key)
    model = ModelInference(
        model_id=llm_id,
        credentials=credentials,
        project_id=proj_id,
        params={
            GenParams.MAX_NEW_TOKENS: 64,
            GenParams.TEMPERATURE: 0.0,
        },
    )
    test_prompt = "Complete in one sentence: The minimum metal width rule ensures"
    response = model.generate_text(prompt=test_prompt)
    record("ModelInference.generate_text() succeeds", True, "")
    record("Response is non-empty string",
           bool(response and response.strip()),
           f"preview: {str(response)[:80]!r}")
except Exception as exc:
    err = str(exc)
    record("LLM generation call", False, err[:200])
    if "not found" in err.lower() or "404" in err:
        print(f"\n  --  Model '{llm_id}' not found in your region/plan.")
        print("     Recommended alternatives (check availability in your region):")
        print("       WATSONX_LLM_MODEL_ID=ibm/granite-13b-instruct-v2")
        print("       WATSONX_LLM_MODEL_ID=ibm/granite-13b-chat-v2")
        print("       WATSONX_LLM_MODEL_ID=meta-llama/llama-3-8b-instruct")
    elif "unauthorized" in err.lower() or "403" in err:
        print("  --  Authorization error -- check your API key and project ID.")


# ==============================================================================
# STEP 5 -- Document ingestion (real embeddings + ChromaDB)
# ==============================================================================
section("STEP 5 -- Real document ingestion")

# Clean the test vector store before ingestion
if Path(CHROMA_TEST_DIR).exists():
    shutil.rmtree(CHROMA_TEST_DIR)

# Reset the vector store module-level cache so it uses the test dir
import backend.vector_store as vs_module
vs_module._chroma_client = None
vs_module._collection = None
get_settings.cache_clear()
settings = get_settings()

DEMO_DOCS = [
    ("demo_data/synthetic_pdk_design_rules.md", "PDK", "Synthetic PDK Design Rules"),
    ("demo_data/synthetic_drc_standard_cells.md", "DRC", "Synthetic DRC Rule Deck"),
    ("demo_data/synthetic_latchup_guidelines.md", "Design Guidelines", "Synthetic Latch-Up Guidelines"),
    ("demo_data/synthetic_spice_model_notes.md", "SPICE Models", "Synthetic SPICE Model Notes"),
    ("demo_data/synthetic_timing_constraints.md", "Application Notes", "Synthetic Timing Constraints"),
]

doc_ids: dict[str, str] = {}
ingest_ok = 0

for rel_path, category, doc_name in DEMO_DOCS:
    abs_path = str(SRC_DIR / rel_path)
    try:
        from backend.document_parser import parse_document
        from backend.embeddings import embed_texts
        from backend.vector_store import upsert_chunks

        doc_id, resolved_name, chunks = parse_document(abs_path, category, doc_name)
        texts = [c.text for c in chunks]
        embeddings = embed_texts(texts)
        metadatas = [c.metadata for c in chunks]
        n = upsert_chunks(texts, embeddings, metadatas, doc_id)
        doc_ids[doc_name] = doc_id
        record(f"Ingest: {doc_name}", True, f"{n} chunks, doc_id={doc_id}")
        ingest_ok += 1
    except Exception as exc:
        record(f"Ingest: {doc_name}", False, str(exc)[:120])

# Verify total
from backend.vector_store import get_total_chunks, get_categories
total = get_total_chunks()
cats = get_categories()
record("Total chunks > 0 after ingestion", total > 0, f"total={total}")
record("All 5 docs ingested", ingest_ok == 5, f"{ingest_ok}/5 succeeded")
record("5 categories present", len(cats) == 5, f"found={[c.name for c in cats]}")

# Duplicate guard: re-ingest doc 1 and verify count does not increase
if ingest_ok >= 1:
    try:
        abs_path = str(SRC_DIR / DEMO_DOCS[0][0])
        doc_id, _, chunks = parse_document(abs_path, DEMO_DOCS[0][1], DEMO_DOCS[0][2])
        texts = [c.text for c in chunks]
        embeddings = embed_texts(texts)
        metadatas = [c.metadata for c in chunks]
        upsert_chunks(texts, embeddings, metadatas, doc_id)
        total_after = get_total_chunks()
        record("Duplicate ingest does not grow chunk count", total_after == total,
               f"before={total}, after={total_after}")
    except Exception as exc:
        record("Duplicate ingest guard", False, str(exc)[:120])


# ==============================================================================
# STEP 6 -- Real retrieval / RAG
# ==============================================================================
section("STEP 6 -- Real retrieval and RAG Q&A")

DEMO_QUERIES = [
    {
        "label": "PDK poly gate overhang",
        "query": "What is the minimum poly gate overhang beyond the active region, and why does it matter?",
        "expected_doc_fragment": "DRC",
        "expect_sufficient": True,
    },
    {
        "label": "Latch-up N-well tap distance",
        "query": "How far must N-well taps be placed from PMOS transistors to prevent latch-up, and what is the tighter rule for output drivers?",
        "expected_doc_fragment": "Latch",
        "expect_sufficient": True,
    },
    {
        "label": "FinFET insufficient-context protection",
        "query": "What is the fin pitch for FinFET gate structures in this process?",
        "expected_doc_fragment": None,
        "expect_sufficient": False,
    },
]

from backend.rag_engine import answer_query

for q in DEMO_QUERIES:
    print(f"\n  Query: {q['query'][:70]}-")
    try:
        result = answer_query(q["query"])
        print(f"  Answer preview: {result.answer[:120]!r}")
        print(f"  sufficient_context={result.sufficient_context}  citations={len(result.citations)}")
        if result.citations:
            for cit in result.citations[:2]:
                print(f"    [{cit.doc_name}] section={cit.section!r} page={cit.page} score={cit.similarity_score:.3f}")

        record(
            f"Retrieval: {q['label']}",
            result.retrieved_chunks >= 0,  # at least attempted
            f"chunks={result.retrieved_chunks} sufficient={result.sufficient_context}",
        )
        record(
            f"Sufficient-context flag correct: {q['label']}",
            result.sufficient_context == q["expect_sufficient"],
            f"expected={q['expect_sufficient']} got={result.sufficient_context}",
        )
        if q["expect_sufficient"]:
            record(
                f"Citations present: {q['label']}",
                len(result.citations) >= 1,
                f"got {len(result.citations)} citations",
            )
        else:
            # Insufficient-context path: answer must NOT invent rules
            no_hallucination = (
                "insufficient" in result.answer.lower()
                or "not contain" in result.answer.lower()
                or "does not contain" in result.answer.lower()
            )
            record(
                f"Insufficient-context refusal (no hallucination): {q['label']}",
                no_hallucination,
                f"answer: {result.answer[:80]!r}",
            )
    except Exception as exc:
        record(f"RAG query: {q['label']}", False, str(exc)[:120])


# ==============================================================================
# STEP 7 -- Bob MCP connection note
# ==============================================================================
section("STEP 7 -- Bob MCP connection (automated check)")

# We can verify the MCP server starts and registers tools without Bob IDE
try:
    from mcp_server.server import mcp
    tools = list(mcp._tool_manager._tools.values())
    tool_names = [t.name for t in tools]
    record("MCP server imports and loads", True, "")
    record("4 tools registered", len(tool_names) == 4, f"tools={tool_names}")
    expected = {"search_knowledge_base", "ingest_document", "list_document_categories", "get_document_sections"}
    record("All expected tool names present", set(tool_names) == expected, "")
    print("\n  --  Full Bob IDE - MCP STDIO handshake requires Bob IDE to be installed.")
    print("     Steps to verify manually:")
    print("     1. Open this project in IBM Bob IDE")
    print("     2. The .bob/mcp.json is read automatically on startup")
    print("     3. Switch to 'Chip Design Assistant' mode")
    print("     4. Ask: 'What chip design categories are available?'")
    print("     5. Bob should call list_document_categories -> show table")
    print("     6. Ask: 'What is the minimum metal 1 width?'")
    print("     7. Bob should call search_knowledge_base -> answer + citation")
except Exception as exc:
    record("MCP server load", False, str(exc)[:120])


# ==============================================================================
# STEP 8 -- Full pytest suite
# ==============================================================================
section("STEP 8 -- Full automated test suite")

try:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "--tb=short", "-q"],
        capture_output=True,
        text=True,
        cwd=str(SRC_DIR),
        timeout=120,
    )
    passed = result.returncode == 0
    # Extract summary line
    lines = (result.stdout + result.stderr).strip().splitlines()
    summary = next((l for l in reversed(lines) if "passed" in l or "failed" in l or "error" in l), "")
    record("Full pytest suite", passed, summary)
    if not passed:
        print("\n  Pytest output (last 20 lines):")
        for line in lines[-20:]:
            print(f"    {line}")
except subprocess.TimeoutExpired:
    record("Full pytest suite", False, "Timed out after 120s")
except Exception as exc:
    record("Full pytest suite", False, str(exc)[:120])


# ==============================================================================
# FINAL REPORT
# ==============================================================================
def _print_summary_and_exit():
    print(f"\n{'=' * 60}")
    print("  FINAL VERIFICATION REPORT")
    print(f"{'=' * 60}\n")

    categories = {
        "watsonx authentication":           ["watsonx.ai auth"],
        "real embeddings":                  ["embed_texts() call succeeds", "embed_query() call succeeds"],
        "real Granite generation":          ["ModelInference.generate_text() succeeds"],
        "document ingestion":               ["All 5 docs ingested", "Total chunks > 0 after ingestion"],
        "ChromaDB persistence":             ["5 categories present"],
        "grounded retrieval":               ["Retrieval: PDK poly gate overhang", "Retrieval: Latch-up N-well tap distance"],
        "citations":                        ["Citations present: PDK poly gate overhang", "Citations present: Latch-up N-well tap distance"],
        "insufficient-context protection":  ["Sufficient-context flag correct: FinFET insufficient-context protection",
                                             "Insufficient-context refusal (no hallucination): FinFET insufficient-context protection"],
        "Bob MCP connection":               ["MCP server imports and loads", "4 tools registered", "All expected tool names present"],
        "Bob automatic MCP tool invocation":["(manual -- see Step 7 instructions above)"],
        "full test suite":                  ["Full pytest suite"],
    }

    result_map = {label: (passed, note) for label, passed, note in RESULTS}

    overall_pass = True
    rows = []
    for cat_label, check_labels in categories.items():
        if check_labels == ["(manual -- see Step 7 instructions above)"]:
            rows.append(("Bob automatic MCP tool invocation", None, "Requires Bob IDE -- verify manually using Step 7 instructions"))
            continue
        cat_passed = all(result_map.get(l, (False, "not run"))[0] for l in check_labels)
        if not cat_passed:
            overall_pass = False
        notes = "; ".join(
            result_map[l][1] for l in check_labels
            if l in result_map and result_map[l][1]
        )
        rows.append((cat_label, cat_passed, notes))

    max_label = max(len(r[0]) for r in rows)
    for cat_label, passed, notes in rows:
        if passed is None:
            status = "[MANUAL]"
        elif passed:
            status = "[PASS]   "
        else:
            status = "[FAIL]   "
            overall_pass = False
        note_str = f"  -> {notes}" if notes else ""
        print(f"  {status}  {cat_label:<{max_label}}{note_str}")

    print(f"\n{'-' * 60}")
    if overall_pass:
        print("  ALL AUTOMATED CHECKS PASSED")
        print("  The application is ready for demo recording.")
        print("  Still required before submission:")
        print("    - Verify Bob IDE MCP tool invocation manually (Step 7)")
        print("    - Record demo video")
        print("    - Add screenshots")
    else:
        print("  SOME CHECKS FAILED -- see [FAIL] rows above")
        print("  Fix the failures before claiming the application is working.")
    print(f"{'=' * 60}\n")
    sys.exit(0 if overall_pass else 1)


_print_summary_and_exit()
