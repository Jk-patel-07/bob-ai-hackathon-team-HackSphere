/**
 * services/api.js — Centralized API service layer.
 *
 * All backend communication goes through this file.
 * No fetch() calls should appear in components or pages.
 *
 * ── URL resolution ───────────────────────────────────────────
 * Development:  Vite dev server (port 5173) proxies each API path
 *               directly to FastAPI on port 8000 — BASE = ''.
 * Production:   FastAPI serves React + API on the same port (8000),
 *               so calls are same-origin — BASE = ''.
 * Override:     Set VITE_API_BASE_URL=http://host:port in .env.local
 *               only if frontend and backend are on different origins.
 *
 * ── No secrets ───────────────────────────────────────────────
 * No watsonx credentials, API keys, or any other secrets belong here.
 */

const BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

// ── Timeout ───────────────────────────────────────────────────
// AI requests can take 20–40 s (retrieval + LLM generation).
// Health/categories checks use a shorter timeout.
const TIMEOUT_AI   = 60_000   // ms
const TIMEOUT_FAST = 10_000   // ms

/**
 * Wraps fetch() with a timeout.
 * Throws a DOMException (AbortError) if the request takes too long.
 */
function fetchWithTimeout(url, options, timeoutMs) {
  const controller = new AbortController()
  const id = setTimeout(() => controller.abort(), timeoutMs)
  return fetch(url, { ...options, signal: controller.signal })
    .finally(() => clearTimeout(id))
}

// ── Core request helper ───────────────────────────────────────

async function request(method, path, body, timeoutMs = TIMEOUT_FAST) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) {
    opts.body = JSON.stringify(body)
  }

  let res
  try {
    res = await fetchWithTimeout(`${BASE}${path}`, opts, timeoutMs)
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Request timed out. The server may be busy — please try again.')
    }
    // Network-level failure (backend offline, DNS failure, etc.)
    throw new Error('Cannot reach the backend. Make sure the server is running.')
  }

  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const errBody = await res.json()
      detail = errBody.detail ?? detail
    } catch {
      // ignore JSON parse failure on error body
    }
    throw new Error(detail)
  }

  let data
  try {
    data = await res.json()
  } catch {
    throw new Error('The server returned an unexpected response format.')
  }

  return data
}

// ── Response normalisers ──────────────────────────────────────
// Guard against missing or malformed fields from the backend.
// Components should never receive null/undefined in required fields.

/**
 * Normalise a Citation object.
 * Ensures all optional fields are either a valid value or null.
 * Never returns NaN for similarity_score.
 */
function normaliseCitation(raw) {
  if (!raw || typeof raw !== 'object') return null
  const score = typeof raw.similarity_score === 'number' && isFinite(raw.similarity_score)
    ? raw.similarity_score
    : 0
  return {
    doc_id:           String(raw.doc_id ?? ''),
    doc_name:         String(raw.doc_name ?? 'Unknown document'),
    category:         String(raw.category ?? ''),
    section:          raw.section != null ? String(raw.section) : null,
    page:             raw.page != null && isFinite(Number(raw.page)) ? Number(raw.page) : null,
    chunk_text:       raw.chunk_text != null ? String(raw.chunk_text) : null,
    similarity_score: score,
  }
}

/**
 * Normalise a SearchResponse object.
 * Returns a safe shape that components can render without null checks.
 */
function normaliseSearchResponse(raw) {
  if (!raw || typeof raw !== 'object') {
    return {
      query:             '',
      answer:            'The server returned an unexpected response.',
      citations:         [],
      retrieved_chunks:  0,
      sufficient_context: false,
      model_used:        'unknown',
    }
  }
  const citations = Array.isArray(raw.citations)
    ? raw.citations.map(normaliseCitation).filter(Boolean)
    : []
  return {
    query:             String(raw.query ?? ''),
    answer:            String(raw.answer ?? ''),
    citations,
    retrieved_chunks:  Number(raw.retrieved_chunks ?? 0),
    sufficient_context: Boolean(raw.sufficient_context),
    model_used:        String(raw.model_used ?? 'unknown'),
  }
}

/**
 * Normalise a HealthResponse object.
 */
function normaliseHealthResponse(raw) {
  if (!raw || typeof raw !== 'object') {
    throw new Error('Malformed health response from backend.')
  }
  return {
    status:             String(raw.status ?? 'unknown'),
    vector_store:       String(raw.vector_store ?? 'unknown'),
    watsonx_configured: Boolean(raw.watsonx_configured),
    llm_model:          String(raw.llm_model ?? ''),
    embedding_model:    String(raw.embedding_model ?? ''),
    total_chunks:       Number(raw.total_chunks ?? 0),
  }
}

// ── Exported API functions ────────────────────────────────────

/**
 * GET /health
 *
 * Checks backend liveness and configuration status.
 *
 * Returns: HealthResponse {
 *   status, vector_store, watsonx_configured,
 *   llm_model, embedding_model, total_chunks
 * }
 */
export async function checkHealth() {
  const raw = await request('GET', '/health', undefined, TIMEOUT_FAST)
  return normaliseHealthResponse(raw)
}

/** @deprecated Use checkHealth() — kept for backwards compatibility */
export function fetchHealth() {
  return checkHealth()
}

/**
 * GET /categories
 *
 * Returns the knowledge-base category summary.
 *
 * Returns: CategoriesResponse {
 *   categories: [{ name, doc_count, chunk_count }],
 *   total_documents, total_chunks
 * }
 */
export async function getCategories() {
  const raw = await request('GET', '/categories', undefined, TIMEOUT_FAST)
  if (!raw || !Array.isArray(raw.categories)) {
    throw new Error('Unexpected response from /categories.')
  }
  return {
    categories:      raw.categories,
    total_documents: Number(raw.total_documents ?? 0),
    total_chunks:    Number(raw.total_chunks ?? 0),
  }
}

/** @deprecated Use getCategories() — kept for backwards compatibility */
export function fetchCategories() {
  return getCategories()
}

/**
 * POST /search
 *
 * Runs a RAG knowledge-base query and returns a grounded answer with citations.
 *
 * @param {string}      query     Natural-language question (min 3 chars)
 * @param {string|null} category  Optional category filter (null = search all)
 * @param {number}      top_k     Max chunks to retrieve (1–20, default 5)
 *
 * Returns: SearchResponse (normalised) {
 *   query, answer, citations, retrieved_chunks,
 *   sufficient_context, model_used
 * }
 */
export async function searchKnowledge(query, category = null, top_k = 5) {
  const raw = await request(
    'POST',
    '/search',
    { query, category, top_k },
    TIMEOUT_AI,           // AI calls can be slow
  )
  return normaliseSearchResponse(raw)
}

/** @deprecated Use searchKnowledge() — kept for backwards compatibility */
export function search(query, category, top_k) {
  return searchKnowledge(query, category, top_k)
}

/**
 * GET /documents/{doc_id}/sections
 *
 * Returns all stored chunks/sections for a specific document by ID.
 *
 * @param {string} docId  The doc_id returned by POST /ingest or GET /documents
 *
 * Returns: DocumentSectionsResponse {
 *   doc_id, doc_name, category,
 *   sections: [{ section, content, page, chunk_index }]
 * }
 */
export async function getDocumentSections(docId) {
  return request(
    'GET',
    `/documents/${encodeURIComponent(docId)}/sections`,
    undefined,
    TIMEOUT_FAST,
  )
}

/** @deprecated Use getDocumentSections() — kept for backwards compatibility */
export function fetchDocumentSections(docId) {
  return getDocumentSections(docId)
}

/**
 * GET /documents
 *
 * Returns a list of all stored documents in the knowledge base.
 */
export async function getDocuments() {
  const raw = await request('GET', '/documents', undefined, TIMEOUT_FAST)
  return {
    documents: Array.isArray(raw?.documents) ? raw.documents : [],
    total_documents: Number(raw?.total_documents ?? 0),
  }
}

/**
 * POST /documents/upload
 *
 * Uploads a document file (.pdf, .md, .txt, .rst) to FastAPI for parsing and ingestion.
 */
export async function uploadDocument(file, category, docName = '') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category', category)
  if (docName && docName.trim()) {
    formData.append('doc_name', docName.trim())
  }

  const controller = new AbortController()
  const id = setTimeout(() => controller.abort(), TIMEOUT_AI)

  let res
  try {
    res = await fetch(`${BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    })
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Upload timed out. The server may be busy processing the document.')
    }
    throw new Error('Cannot reach the backend server.')
  } finally {
    clearTimeout(id)
  }

  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const errBody = await res.json()
      detail = errBody.detail ?? detail
    } catch {
      // ignore
    }
    throw new Error(detail)
  }

  return res.json()
}

/**
 * DELETE /documents/{doc_id}
 *
 * Deletes a document and all its indexed chunks from ChromaDB.
 */
export async function deleteDocument(docId) {
  return request(
    'DELETE',
    `/documents/${encodeURIComponent(docId)}`,
    undefined,
    TIMEOUT_FAST,
  )
}

