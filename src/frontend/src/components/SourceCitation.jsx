/**
 * SourceCitation — renders one citation/source from the /search response.
 *
 * Props:
 *   citation  { doc_name, doc_id, category, section, page,
 *               similarity_score, chunk_text }
 *   index     {number}  0-based position in the citations array
 *
 * IMPORTANT: Only renders values actually returned by the backend.
 * Never fabricates document names, page numbers, sections, or confidence values.
 */

function DocIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">
      <path d="M3 1.5h4.5L10 4v7.5H3V1.5z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" fill="none"/>
      <path d="M7.5 1.5V4H10" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" fill="none"/>
      <line x1="4.5" y1="6" x2="8.5" y2="6" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="4.5" y1="8" x2="8.5" y2="8" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="4.5" y1="10" x2="6.5" y2="10" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
    </svg>
  )
}

export default function SourceCitation({ citation, index }) {
  const pct = Math.round(citation.similarity_score * 100)
  const barCls =
    pct >= 70 ? 'conf-bar--high' : pct >= 45 ? 'conf-bar--mid' : 'conf-bar--low'

  return (
    <article className="source-citation" aria-label={`Source ${index + 1}: ${citation.doc_name}`}>
      <div className="citation-header">
        <span className="citation-doc-icon">
          <DocIcon />
        </span>
        <span className="citation-index" aria-hidden="true">[{index + 1}]</span>
        <span className="citation-doc-name">{citation.doc_name}</span>
        <span className="citation-category">{citation.category}</span>
      </div>

      {(citation.section || citation.page != null) && (
        <div className="citation-meta">
          {citation.section && (
            <span className="citation-meta-item">
              <span className="citation-meta-label">Section</span>
              {citation.section}
            </span>
          )}
          {citation.page != null && (
            <span className="citation-meta-item">
              <span className="citation-meta-label">Page</span>
              {citation.page}
            </span>
          )}
        </div>
      )}

      <div className="confidence-row" aria-label={`Relevance: ${pct}%`}>
        <span className="confidence-label">Relevance</span>
        <div className="confidence-track" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
          <div
            className={`confidence-bar ${barCls}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="confidence-value">{pct}%</span>
      </div>

      {citation.chunk_text && (
        <details className="citation-excerpt">
          <summary>Source excerpt</summary>
          <p className="citation-excerpt-text">{citation.chunk_text}</p>
        </details>
      )}
    </article>
  )
}
