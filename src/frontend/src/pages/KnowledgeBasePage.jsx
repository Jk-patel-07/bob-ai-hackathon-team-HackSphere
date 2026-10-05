/**
 * KnowledgeBasePage — displays knowledge base statistics.
 *
 * Data is fetched live from GET /categories.
 * Uses loading/empty states until backend data is available.
 * Does NOT hardcode fake statistics.
 */
import { useEffect, useState } from 'react'
import { getCategories } from '../services/api'

/* ── Icon helpers ── */
function DocCountIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M4 2h5.5L12 4.5V14H4V2z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" fill="none"/>
      <path d="M9.5 2v2.5H12" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" fill="none"/>
      <line x1="6" y1="7" x2="10" y2="7" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="6" y1="9.5" x2="10" y2="9.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  )
}

function CategoryIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <rect x="2" y="2" width="5" height="5" rx="1" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <rect x="9" y="2" width="5" height="5" rx="1" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <rect x="2" y="9" width="5" height="5" rx="1" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <rect x="9" y="9" width="5" height="5" rx="1" stroke="currentColor" strokeWidth="1.4" fill="none"/>
    </svg>
  )
}

function ChunksIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <rect x="2" y="3" width="12" height="10" rx="1.5" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <line x1="5" y1="6.5" x2="11" y2="6.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="5" y1="9" x2="9" y2="9" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  )
}

function StatusIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <path d="M5 8l2 2 4-4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function CategoryCardIcon({ name }) {
  // Simple category-specific icons
  const icons = {
    PDK: (
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
        <rect x="3" y="3" width="8" height="8" rx="1" stroke="currentColor" strokeWidth="1.3" fill="none"/>
        <rect x="4.5" y="4.5" width="5" height="5" rx="0.5" fill="currentColor" opacity="0.3"/>
        <line x1="5" y1="3" x2="5" y2="1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
        <line x1="7" y1="3" x2="7" y2="1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
        <line x1="9" y1="3" x2="9" y2="1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      </svg>
    ),
    DRC: (
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
        <path d="M7 1.5L12.5 10.5H1.5L7 1.5Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" fill="none"/>
        <line x1="7" y1="5.5" x2="7" y2="7.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
        <circle cx="7" cy="9" r="0.6" fill="currentColor"/>
      </svg>
    ),
  }
  const fallback = (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <rect x="2" y="2.5" width="10" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.3" fill="none"/>
      <line x1="4" y1="5.5" x2="10" y2="5.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="4" y1="7.5" x2="8" y2="7.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
    </svg>
  )
  return icons[name] ?? fallback
}

function ErrorIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <line x1="7" y1="4.5" x2="7" y2="7.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      <circle cx="7" cy="9.5" r="0.65" fill="currentColor"/>
    </svg>
  )
}

function EmptyIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" strokeWidth="1.6" fill="none"/>
      <line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      <line x1="12" y1="8" x2="12" y2="16" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
    </svg>
  )
}

export default function KnowledgeBasePage() {
  const [data, setData]       = useState(null)
  const [error, setError]     = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getCategories()
      .then((d) => { setData(d); setLoading(false) })
      .catch((e) => { setError(e.message); setLoading(false) })
  }, [])

  const kbStatus = data
    ? (data.total_chunks > 0 ? 'ok' : 'warn')
    : (error ? 'err' : null)

  const statusLabel = { ok: 'Operational', warn: 'Empty', err: 'Unavailable' }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Knowledge Base</h1>
        <p className="page-subtitle">Engineering knowledge available to the AI assistant</p>
      </div>

      <div className="page-inner">
        {/* Error banner */}
        {error && (
          <div className="page-error" role="alert">
            <span className="page-error-icon"><ErrorIcon /></span>
            <span>Could not load knowledge base: {error}</span>
          </div>
        )}

        {/* Stats row */}
        <div className="stats-row">
          {/* Documents */}
          <div className="stat-card">
            <span className="stat-card-icon"><DocCountIcon /></span>
            {loading
              ? <span className="skeleton-line skeleton-line--lg" />
              : <span className="stat-value">{data?.total_documents ?? '—'}</span>
            }
            <span className="stat-label">Documents</span>
          </div>

          {/* Categories */}
          <div className="stat-card">
            <span className="stat-card-icon"><CategoryIcon /></span>
            {loading
              ? <span className="skeleton-line skeleton-line--lg" />
              : <span className="stat-value">{data?.categories.length ?? '—'}</span>
            }
            <span className="stat-label">Categories</span>
          </div>

          {/* Chunks */}
          <div className="stat-card">
            <span className="stat-card-icon"><ChunksIcon /></span>
            {loading
              ? <span className="skeleton-line skeleton-line--lg" />
              : <span className="stat-value">{data?.total_chunks ?? '—'}</span>
            }
            <span className="stat-label">Indexed Chunks</span>
          </div>

          {/* KB Status */}
          <div className="stat-card">
            <span className="stat-card-icon"><StatusIcon /></span>
            {loading
              ? <span className="skeleton-line skeleton-line--lg" />
              : <span className="stat-value stat-value--dash">
                  {kbStatus ? (
                    <span className={`stat-status stat-status--${kbStatus}`}>
                      <span className="stat-status-dot" aria-hidden="true" />
                      {statusLabel[kbStatus]}
                    </span>
                  ) : '—'}
                </span>
            }
            <span className="stat-label">Knowledge Base Status</span>
          </div>
        </div>

        {/* Empty state */}
        {!loading && !error && data?.categories.length === 0 && (
          <div className="empty-page-state">
            <div className="empty-page-icon"><EmptyIcon /></div>
            <h3>No documents ingested yet</h3>
            <p>
              Run <code>python scripts/seed_demo_data.py</code> from the{' '}
              <code>src/</code> directory to load synthetic demo data, then refresh this page.
            </p>
          </div>
        )}

        {/* Categories grid */}
        {!loading && data && data.categories.length > 0 && (
          <>
            <h2 className="section-title">Categories</h2>
            <div className="category-grid">
              {data.categories.map((cat) => (
                <div key={cat.name} className="category-card">
                  <div className="category-card-header">
                    <span className="category-card-icon">
                      <CategoryCardIcon name={cat.name} />
                    </span>
                    <span className="category-card-name">{cat.name}</span>
                  </div>
                  <div className="category-card-stats">
                    <div className="category-stat">
                      <span className="category-stat-value">{cat.doc_count}</span>
                      <span className="category-stat-label">{cat.doc_count === 1 ? 'Document' : 'Documents'}</span>
                    </div>
                    <div className="category-stat">
                      <span className="category-stat-value">{cat.chunk_count}</span>
                      <span className="category-stat-label">Chunks</span>
                    </div>
                  </div>
                  <div className="category-card-bar-row">
                    <div className="category-card-bar" role="progressbar"
                      aria-valuenow={data.total_chunks > 0 ? Math.round((cat.chunk_count / data.total_chunks) * 100) : 0}
                      aria-valuemin={0} aria-valuemax={100}>
                      <div
                        className="category-card-bar-fill"
                        style={{
                          width: data.total_chunks > 0
                            ? `${Math.round((cat.chunk_count / data.total_chunks) * 100)}%`
                            : '0%',
                        }}
                      />
                    </div>
                    <span className="category-card-pct">
                      {data.total_chunks > 0
                        ? `${Math.round((cat.chunk_count / data.total_chunks) * 100)}%`
                        : '0%'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Loading skeleton for categories */}
        {loading && (
          <div className="category-grid" aria-busy="true" aria-label="Loading categories">
            {[1, 2, 3, 4].map((n) => (
              <div key={n} className="category-card category-card--skeleton">
                <div className="skeleton-line skeleton-line--md" />
                <div className="skeleton-line skeleton-line--sm" />
                <div className="skeleton-line skeleton-line--full" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
