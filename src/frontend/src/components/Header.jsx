import { useHealth } from '../hooks/useHealth'
import StatusIndicator from './StatusIndicator'

export default function Header() {
  const health = useHealth()

  return (
    <header className="app-header">
      <div className="header-left">
        <div className="header-logo">⬡</div>
        <div>
          <h1 className="header-title">Chip Design Knowledge Assistant</h1>
          <p className="header-subtitle">AI-powered semiconductor design knowledge retrieval</p>
        </div>
      </div>
      <StatusIndicator status={health.status} detail={health.detail} />
    </header>
  )
}

