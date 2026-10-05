/**
 * DocumentsPage — Complete Document Management.
 *
 * Capabilities:
 *   - Fetch and display real indexed documents via GET /documents
 *   - Upload new documents (.pdf, .md, .txt, .rst) via POST /documents/upload
 *   - Filter documents by category
 *   - Inspect document sections via GET /documents/{doc_id}/sections
 *   - Remove document & chunks via DELETE /documents/{doc_id}
 */
import { useEffect, useState } from 'react'
import {
  deleteDocument,
  getDocumentSections,
  getDocuments,
  uploadDocument,
} from '../services/api'

const CATEGORY_OPTIONS = [
  'PDK',
  'DRC',
  'Design Guidelines',
  'Application Notes',
  'SPICE Models',
  'Other',
]

function ErrorIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.4" fill="none" />
      <line x1="7" y1="4.5" x2="7" y2="7.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <circle cx="7" cy="9.5" r="0.65" fill="currentColor" />
    </svg>
  )
}

function EmptyDocIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M6 3h8.5L18 6.5V21H6V3z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" fill="none" />
      <path d="M14.5 3v3.5H18" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" fill="none" />
      <line x1="9" y1="10" x2="15" y2="10" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <line x1="9" y1="13" x2="15" y2="13" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <line x1="9" y1="16" x2="12" y2="16" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  )
}

function formatDate(isoStr) {
  if (!isoStr) return null
  try {
    const d = new Date(isoStr)
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  } catch {
    return null
  }
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [categoryFilter, setCategoryFilter] = useState('All')

  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadFile, setUploadFile] = useState(null)
  const [uploadCategory, setUploadCategory] = useState('PDK')
  const [uploadDocName, setUploadDocName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [uploadSuccess, setUploadSuccess] = useState(null)

  // Sections inspector modal state
  const [inspectDoc, setInspectDoc] = useState(null)
  const [inspectSections, setInspectSections] = useState(null)
  const [loadingSections, setLoadingSections] = useState(false)

  // Delete modal state
  const [deleteConfirmDoc, setDeleteConfirmDoc] = useState(null)
  const [deleting, setDeleting] = useState(false)

  function loadData() {
    setLoading(true)
    setError(null)
    getDocuments()
      .then((res) => {
        setDocuments(res.documents)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }

  useEffect(() => {
    loadData()
  }, [])

  // Close modals on Escape key press
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        setShowUploadModal(false)
        setInspectDoc(null)
        setDeleteConfirmDoc(null)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Derived category list from existing documents + standard defaults
  const availableCategories = Array.from(
    new Set([
      'All',
      ...CATEGORY_OPTIONS,
      ...documents.map((d) => d.category).filter(Boolean),
    ])
  )

  const filteredDocs =
    categoryFilter === 'All'
      ? documents
      : documents.filter((d) => d.category === categoryFilter)

  // ── Upload Handler ─────────────────────────────────────────
  async function handleUploadSubmit(e) {
    e.preventDefault()
    if (!uploadFile) {
      setUploadError('Please select a file to upload.')
      return
    }

    setUploading(true)
    setUploadError(null)
    setUploadSuccess(null)

    try {
      const res = await uploadDocument(uploadFile, uploadCategory, uploadDocName)
      setUploadSuccess(`Successfully ingested '${res.doc_name}' (${res.chunks_created} chunks).`)
      setUploadFile(null)
      setUploadDocName('')
      loadData()
      setTimeout(() => {
        setShowUploadModal(false)
        setUploadSuccess(null)
      }, 1500)
    } catch (err) {
      setUploadError(err.message ?? 'Document upload failed.')
    } finally {
      setUploading(false)
    }
  }

  // ── Inspect Sections Handler ──────────────────────────────
  async function handleRowClick(doc) {
    setInspectDoc(doc)
    setInspectSections(null)
    setLoadingSections(true)
    try {
      const res = await getDocumentSections(doc.doc_id)
      setInspectSections(res.sections ?? [])
    } catch {
      setInspectSections([])
    } finally {
      setLoadingSections(false)
    }
  }

  // ── Delete Handler ────────────────────────────────────────
  async function handleDeleteExecute() {
    if (!deleteConfirmDoc) return
    setDeleting(true)
    try {
      await deleteDocument(deleteConfirmDoc.doc_id)
      setDeleteConfirmDoc(null)
      loadData()
    } catch (err) {
      alert(`Failed to delete document: ${err.message}`)
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Documents</h1>
            <p className="page-subtitle">Manage semiconductor knowledge sources & rule decks</p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => {
              setUploadError(null)
              setUploadSuccess(null)
              setShowUploadModal(true)
            }}
          >
            <span aria-hidden="true">+</span> Add Document
          </button>
        </div>
      </div>

      <div className="page-inner">
        {/* Toolbar & Category Filter */}
        <div className="toolbar-row">
          <div className="filter-group">
            <label htmlFor="category-filter" className="form-label" style={{ margin: 0 }}>
              Category:
            </label>
            <select
              id="category-filter"
              className="form-select"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              {availableCategories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
          <span className="text-muted" style={{ fontSize: '12px' }}>
            {filteredDocs.length} {filteredDocs.length === 1 ? 'document' : 'documents'} found
          </span>
        </div>

        {/* Error */}
        {error && (
          <div className="page-error" role="alert">
            <span className="page-error-icon">
              <ErrorIcon />
            </span>
            <span>Could not load documents: {error}</span>
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div className="doc-table-wrap" aria-busy="true" aria-label="Loading documents">
            <table className="doc-table">
              <thead>
                <tr>
                  <th scope="col">Document</th>
                  <th scope="col">Category</th>
                  <th scope="col">Status</th>
                  <th scope="col">Chunks</th>
                  <th scope="col">Added</th>
                  <th scope="col" style={{ textAlign: 'right' }}>
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3].map((n) => (
                  <tr key={n} className="doc-row">
                    <td>
                      <span className="skeleton-line skeleton-line--md" />
                    </td>
                    <td>
                      <span className="skeleton-line skeleton-line--sm" />
                    </td>
                    <td>
                      <span className="skeleton-line skeleton-line--sm" />
                    </td>
                    <td>
                      <span className="skeleton-line skeleton-line--sm" />
                    </td>
                    <td>
                      <span className="skeleton-line skeleton-line--sm" />
                    </td>
                    <td>
                      <span className="skeleton-line skeleton-line--sm" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && filteredDocs.length === 0 && (
          <div className="empty-page-state">
            <div className="empty-page-icon">
              <EmptyDocIcon />
            </div>
            <h3>No documents indexed yet</h3>
            <p>
              Click <strong>+ Add Document</strong> above to upload a PDF or Markdown file,
              or run <code>python scripts/seed_demo_data.py</code> to load synthetic demo files.
            </p>
          </div>
        )}

        {/* Documents table */}
        {!loading && filteredDocs.length > 0 && (
          <div className="doc-table-wrap">
            <table className="doc-table">
              <thead>
                <tr>
                  <th scope="col">Document</th>
                  <th scope="col">Category</th>
                  <th scope="col">Status</th>
                  <th scope="col">Chunks</th>
                  <th scope="col">Added</th>
                  <th scope="col" style={{ textAlign: 'right' }}>
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.map((doc) => (
                  <tr key={doc.doc_id} className="doc-row">
                    <td
                      className="doc-cell-name"
                      onClick={() => handleRowClick(doc)}
                      style={{ cursor: 'pointer' }}
                      title="Click to inspect document sections"
                    >
                      <span className="doc-name">{doc.doc_name}</span>
                      {doc.file_name && (
                        <span className="text-muted" style={{ fontSize: '11px' }}>
                          {doc.file_name}
                        </span>
                      )}
                    </td>
                    <td>
                      <span className="doc-category-tag">{doc.category}</span>
                    </td>
                    <td>
                      <span className="doc-status doc-status--ok">Indexed</span>
                    </td>
                    <td className="doc-cell-num">{doc.chunk_count}</td>
                    <td className="doc-cell-date">
                      {formatDate(doc.created_at) ?? <span className="muted">—</span>}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="action-btn-sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleRowClick(doc)
                        }}
                        style={{ marginRight: '6px' }}
                      >
                        Inspect
                      </button>
                      <button
                        className="action-btn-sm action-btn-sm--danger"
                        onClick={(e) => {
                          e.stopPropagation()
                          setDeleteConfirmDoc(doc)
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Upload Modal ────────────────────────────────────────── */}
      {showUploadModal && (
        <div className="modal-overlay" onClick={() => setShowUploadModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Upload Knowledge Document</h3>
              <button className="modal-close-btn" onClick={() => setShowUploadModal(false)}>
                ✕
              </button>
            </div>
            <form onSubmit={handleUploadSubmit}>
              <div className="modal-body">
                {uploadError && (
                  <div className="page-error" role="alert">
                    <span className="page-error-icon">
                      <ErrorIcon />
                    </span>
                    <span>{uploadError}</span>
                  </div>
                )}
                {uploadSuccess && (
                  <div
                    style={{
                      padding: '10px 14px',
                      background: 'var(--green-bg)',
                      border: '1px solid var(--green-border)',
                      color: '#166534',
                      borderRadius: 'var(--r-md)',
                      fontSize: '13px',
                      fontWeight: '600',
                    }}
                  >
                    ✅ {uploadSuccess}
                  </div>
                )}

                <div className="form-group">
                  <label className="form-label">Document File (.pdf, .md, .txt, .rst)</label>
                  <label className="file-drop-zone">
                    <input
                      type="file"
                      accept=".pdf,.md,.txt,.rst"
                      onChange={(e) => setUploadFile(e.target.files[0] ?? null)}
                      style={{ display: 'none' }}
                      disabled={uploading}
                    />
                    <div className="file-drop-text">
                      {uploadFile ? uploadFile.name : 'Click or drop a file to upload'}
                    </div>
                    <div className="file-drop-sub">
                      {uploadFile
                        ? `${(uploadFile.size / 1024).toFixed(1)} KB`
                        : 'Supported formats: PDF, Markdown, TXT (Max 15 MB)'}
                    </div>
                  </label>
                </div>

                <div className="form-group">
                  <label htmlFor="upload-category" className="form-label">
                    Category
                  </label>
                  <select
                    id="upload-category"
                    className="form-select"
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value)}
                    disabled={uploading}
                  >
                    {CATEGORY_OPTIONS.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="upload-doc-name" className="form-label">
                    Document Name (Optional)
                  </label>
                  <input
                    id="upload-doc-name"
                    type="text"
                    className="form-input"
                    placeholder="e.g. ST130 DRM Rule Deck v2.1"
                    value={uploadDocName}
                    onChange={(e) => setUploadDocName(e.target.value)}
                    disabled={uploading}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowUploadModal(false)}
                  disabled={uploading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={uploading || !uploadFile}
                >
                  {uploading ? 'Indexing document…' : 'Upload & Index'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Sections Inspection Modal ───────────────────────────── */}
      {inspectDoc && (
        <div className="modal-overlay" onClick={() => setInspectDoc(null)}>
          <div
            className="modal-card modal-card--lg"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <h3 className="modal-title">{inspectDoc.doc_name}</h3>
                <span className="doc-category-tag" style={{ marginTop: '4px' }}>
                  {inspectDoc.category}
                </span>
              </div>
              <button className="modal-close-btn" onClick={() => setInspectDoc(null)}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div
                style={{
                  display: 'flex',
                  gap: '16px',
                  fontSize: '12px',
                  color: 'var(--text-secondary)',
                  borderBottom: '1px solid var(--border)',
                  paddingBottom: '12px',
                }}
              >
                <span>
                  <strong>ID:</strong> <code>{inspectDoc.doc_id}</code>
                </span>
                <span>
                  <strong>Chunks:</strong> {inspectDoc.chunk_count}
                </span>
                {inspectDoc.file_name && (
                  <span>
                    <strong>File:</strong> {inspectDoc.file_name}
                  </span>
                )}
              </div>

              {loadingSections && (
                <div style={{ padding: '24px', textAlign: 'center' }}>
                  Loading document sections…
                </div>
              )}

              {!loadingSections && inspectSections && inspectSections.length === 0 && (
                <div style={{ padding: '24px', textAlign: 'center' }}>
                  No detailed sections available for this document.
                </div>
              )}

              {!loadingSections && inspectSections && inspectSections.length > 0 && (
                <div
                  style={{
                    maxHeight: '400px',
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                  }}
                >
                  {inspectSections.map((sec, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '12px',
                        background: 'var(--surface-2)',
                        borderRadius: 'var(--r-md)',
                        border: '1px solid var(--border)',
                      }}
                    >
                      <div
                        style={{
                          fontWeight: '700',
                          fontSize: '13px',
                          color: 'var(--text-primary)',
                          marginBottom: '6px',
                        }}
                      >
                        {sec.section ?? `Chunk #${sec.chunk_index + 1}`}
                        {sec.page != null && (
                          <span
                            style={{
                              fontWeight: 'normal',
                              fontSize: '11px',
                              color: 'var(--text-muted)',
                              marginLeft: '8px',
                            }}
                          >
                            (Page {sec.page})
                          </span>
                        )}
                      </div>
                      <p
                        style={{
                          fontSize: '12px',
                          lineHeight: '1.5',
                          margin: 0,
                          color: 'var(--text-secondary)',
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        {sec.content}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setInspectDoc(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Delete Confirmation Modal ──────────────────────────── */}
      {deleteConfirmDoc && (
        <div className="modal-overlay" onClick={() => setDeleteConfirmDoc(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Delete Document</h3>
              <button
                className="modal-close-btn"
                onClick={() => setDeleteConfirmDoc(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <p style={{ margin: 0, fontSize: '14px', color: 'var(--text-primary)' }}>
                Are you sure you want to remove <strong>{deleteConfirmDoc.doc_name}</strong> from
                the knowledge base?
              </p>
              <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>
                This will delete all {deleteConfirmDoc.chunk_count} indexed chunks from ChromaDB.
                This action cannot be undone.
              </p>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setDeleteConfirmDoc(null)}
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDeleteExecute}
                disabled={deleting}
              >
                {deleting ? 'Deleting…' : 'Delete Document'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
