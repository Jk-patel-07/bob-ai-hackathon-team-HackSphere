/**
 * CitationCard — renders one Citation object from the /search response.
 * Shows doc name, section, page, similarity score, and truncated chunk text.
 */
export default function CitationCard({ citation, index }) {
  const pct = Math.round(citation.similarity_score * 100)
  const barWidth = `${pct}%`
  const barCls =
    pct >= 70 ? 'confidence-bar-high' : pct >= 45 ? 'confidence-bar-mid' : 'confidence-bar-low'

  return (
    <div className="citation-card">
      <div className="citation-header">
        <span className="citation-index">[{index + 1}]</span>
        <span className="citation-doc-name">{citation.doc_name}</span>
        <span className="citation-category">{citation.category}</span>
      </div>

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

      <div className="confidence-row">
        <span className="confidence-label">Relevance</span>
        <div className="confidence-track">
          <div className={`confidence-bar ${barCls}`} style={{ width: barWidth }} />
        </div>
        <span className="confidence-value">{pct}%</span>
      </div>

      <details className="citation-chunk">
        <summary>Source excerpt</summary>
        <p className="citation-chunk-text">{citation.chunk_text}</p>
      </details>
    </div>
  )
}
