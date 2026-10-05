/**
 * StatusIndicator — reusable backend connection status badge.
 *
 * Props:
 *   status   'checking' | 'connected' | 'degraded' | 'disconnected'
 *   detail   optional detail string (e.g. "128 chunks · granite-13b-chat-v2")
 */
export default function StatusIndicator({ status, detail }) {
  const MAP = {
    checking:     { label: 'Connecting…',   cls: 'status--checking' },
    connected:    { label: 'Connected',      cls: 'status--connected' },
    degraded:     { label: 'Degraded',       cls: 'status--degraded' },
    disconnected: { label: 'Disconnected',   cls: 'status--disconnected' },
  }

  const { label, cls } = MAP[status] ?? MAP.checking

  return (
    <div className={`status-indicator ${cls}`}>
      <span className="status-dot" aria-hidden="true" />
      <div className="status-text">
        <span className="status-label">{label}</span>
        {detail && <span className="status-detail">{detail}</span>}
      </div>
    </div>
  )
}
