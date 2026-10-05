/**
 * AssistantMessage — renders a single assistant turn.
 *
 * Props:
 *   result  SearchResponse {
 *     answer, citations, sufficient_context,
 *     retrieved_chunks, model_used
 *   }
 */
import SourceCitation from './SourceCitation'

function BotAvatar() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <rect x="3" y="3" width="8" height="8" rx="1" stroke="currentColor" strokeWidth="1.3" fill="none"/>
      <line x1="5" y1="3" x2="5" y2="1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="7" y1="3" x2="7" y2="1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="9" y1="3" x2="9" y2="1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="5" y1="11" x2="5" y2="12.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="7" y1="11" x2="7" y2="12.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="9" y1="11" x2="9" y2="12.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="3" y1="5" x2="1.5" y2="5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="3" y1="7" x2="1.5" y2="7" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="3" y1="9" x2="1.5" y2="9" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="11" y1="5" x2="12.5" y2="5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="11" y1="7" x2="12.5" y2="7" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <line x1="11" y1="9" x2="12.5" y2="9" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
      <rect x="4.5" y="4.5" width="5" height="5" rx="0.5" fill="currentColor" opacity="0.25"/>
    </svg>
  )
}

function WarningIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M7 2L12.5 11.5H1.5L7 2Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" fill="none"/>
      <line x1="7" y1="6" x2="7" y2="8.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
      <circle cx="7" cy="10" r="0.6" fill="currentColor"/>
    </svg>
  )
}

export default function AssistantMessage({ result }) {
  const insufficient = !result.sufficient_context

  return (
    <div className={`assistant-message ${insufficient ? 'assistant-message--warn' : ''}`}>
      {/* Answer bubble */}
      <div className="answer-bubble">
        <div className="assistant-avatar" aria-hidden="true">
          <BotAvatar />
        </div>
        <div className="answer-content">
          {insufficient && (
            <div className="insufficient-banner" role="status" aria-live="polite">
              <span className="insufficient-banner-icon">
                <WarningIcon />
              </span>
              <span>
                <span className="insufficient-title">
                  Insufficient information in the knowledge base
                </span>
                <span className="insufficient-body">
                  The relevant documentation may not have been ingested yet.
                  Add the appropriate PDK, DRC, or design-guideline documents to improve answers.
                </span>
              </span>
            </div>
          )}
          <p className="answer-text">{result.answer}</p>
          <div className="answer-meta" aria-label="Response metadata">
            <span className="answer-meta-item">
              <span className="answer-meta-label">Model</span>
              <code>{result.model_used}</code>
            </span>
            <span className="answer-meta-item">
              <span className="answer-meta-label">Retrieved</span>
              {result.retrieved_chunks} chunk{result.retrieved_chunks !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      </div>

      {/* Sources */}
      {result.citations && result.citations.length > 0 && (
        <div className="citations-section" aria-label="Source documents">
          <h4 className="citations-heading">Sources</h4>
          <div className="citations-list">
            {result.citations.map((c, i) => (
              <SourceCitation key={`${c.doc_id}-${i}`} citation={c} index={i} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
