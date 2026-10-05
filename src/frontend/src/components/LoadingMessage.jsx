/**
 * LoadingMessage — animated indicator shown while the backend processes a query.
 * Two-phase text: searching → generating.
 */
import { useEffect, useState } from 'react'

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

const PHASES = [
  'Searching engineering knowledge…',
  'Generating grounded answer…',
]

export default function LoadingMessage() {
  const [phase, setPhase] = useState(0)

  // Advance to phase 1 after 1.8 s — realistic for RAG retrieval + LLM call
  useEffect(() => {
    const t = setTimeout(() => setPhase(1), 1800)
    return () => clearTimeout(t)
  }, [])

  return (
    <div className="loading-message" role="status" aria-live="polite" aria-label={PHASES[phase]}>
      <div className="loading-avatar" aria-hidden="true">
        <BotAvatar />
      </div>
      <div className="loading-bubble">
        <span className="loading-dots" aria-hidden="true">
          <span /><span /><span />
        </span>
        <span className="loading-text">{PHASES[phase]}</span>
      </div>
    </div>
  )
}
