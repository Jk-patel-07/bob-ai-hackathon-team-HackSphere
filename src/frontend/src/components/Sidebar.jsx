/**
 * Sidebar — left navigation panel.
 *
 * Props:
 *   currentPage  {'chat'|'knowledge'|'documents'}
 *   onNavigate   (page: string) => void
 *   onNewChat    () => void
 */
import { useHealth } from '../hooks/useHealth'
import StatusIndicator from './StatusIndicator'

/* ── SVG icon components (inline, no external deps) ── */
function ChipIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <rect x="4" y="4" width="8" height="8" rx="1" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <line x1="6" y1="4" x2="6" y2="2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="8" y1="4" x2="8" y2="2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="10" y1="4" x2="10" y2="2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="6" y1="12" x2="6" y2="14" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="8" y1="12" x2="8" y2="14" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="10" y1="12" x2="10" y2="14" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="4" y1="6" x2="2" y2="6" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="4" y1="8" x2="2" y2="8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="4" y1="10" x2="2" y2="10" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="12" y1="6" x2="14" y2="6" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="12" y1="8" x2="14" y2="8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="12" y1="10" x2="14" y2="10" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <rect x="5.5" y="5.5" width="5" height="5" rx="0.5" fill="currentColor" opacity="0.3"/>
    </svg>
  )
}

function AssistantIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <path d="M5 8.5c0-1.657 1.343-3 3-3s3 1.343 3 3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" fill="none"/>
      <circle cx="8" cy="6" r="0.8" fill="currentColor"/>
    </svg>
  )
}

function KBIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <rect x="2" y="3" width="12" height="10" rx="1.5" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <line x1="5" y1="6.5" x2="11" y2="6.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="5" y1="9" x2="9" y2="9" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  )
}

function DocumentsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M4 2h5.5L12 4.5V14H4V2z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" fill="none"/>
      <path d="M9.5 2v2.5H12" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" fill="none"/>
      <line x1="6" y1="7" x2="10" y2="7" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="6" y1="9.5" x2="10" y2="9.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="6" y1="12" x2="8.5" y2="12" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  )
}

const NAV_ITEMS = [
  { id: 'chat',      label: 'Assistant',      Icon: AssistantIcon },
  { id: 'knowledge', label: 'Knowledge Base', Icon: KBIcon        },
  { id: 'documents', label: 'Documents',      Icon: DocumentsIcon },
]

export default function Sidebar({ currentPage, onNavigate, onNewChat }) {
  const health = useHealth()

  return (
    <aside className="sidebar" role="navigation" aria-label="Application sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-logo" aria-hidden="true">
          <ChipIcon />
        </div>
        <div className="sidebar-brand-text">
          <span className="sidebar-product">Chip Design</span>
          <span className="sidebar-product-sub">Knowledge Assistant</span>
        </div>
      </div>

      {/* New Chat */}
      <div className="sidebar-actions">
        <button className="new-chat-btn" onClick={onNewChat} aria-label="Start new chat">
          <span className="new-chat-icon" aria-hidden="true">+</span>
          New Chat
        </button>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav" aria-label="Main navigation">
        <ul className="sidebar-nav-list" role="list">
          {NAV_ITEMS.map(({ id, label, Icon }) => (
            <li key={id} role="listitem">
              <button
                className={`nav-item ${currentPage === id ? 'nav-item--active' : ''}`}
                onClick={() => onNavigate(id)}
                aria-current={currentPage === id ? 'page' : undefined}
              >
                <span className="nav-icon">
                  <Icon />
                </span>
                <span className="nav-label">{label}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer — status + attribution */}
      <div className="sidebar-footer">
        <StatusIndicator status={health.status} detail={health.detail} />
        <div className="sidebar-attribution" aria-label="Powered by IBM Bob">
          Powered by IBM Bob
        </div>
      </div>
    </aside>
  )
}
