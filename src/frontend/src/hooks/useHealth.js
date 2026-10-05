/**
 * useHealth — polls GET /health on mount and every 30 s.
 *
 * Returns {
 *   status: 'checking' | 'connected' | 'degraded' | 'disconnected',
 *   detail: string,      — short human-readable detail line
 *   health: object|null  — raw normalised HealthResponse (or null)
 * }
 *
 * When disconnected, retries every 10 s (up to 3 quick retries) before
 * settling back to the 30 s interval.  This gives fast recovery when the
 * backend restarts without spamming it under normal operation.
 */
import { useEffect, useRef, useState } from 'react'
import { checkHealth } from '../services/api'

export function useHealth(pollIntervalMs = 30_000) {
  const [state, setState] = useState({
    status: 'checking',
    detail: '',
    health: null,
  })

  // Track retry state without causing extra renders
  const retryCount  = useRef(0)
  const retryTimer  = useRef(null)

  useEffect(() => {
    let cancelled = false

    function scheduleRetry() {
      if (cancelled) return
      if (retryTimer.current) clearTimeout(retryTimer.current)
      // Quick retries: 10 s, 10 s, 10 s, then back to normal interval
      const delay = retryCount.current < 3 ? 10_000 : pollIntervalMs
      retryTimer.current = setTimeout(poll, delay)
    }

    function poll() {
      if (cancelled) return
      checkHealth()
        .then((h) => {
          if (cancelled) return
          retryCount.current = 0  // reset on success
          const configured = h.provider_configured ?? h.watsonx_configured
          const providerName = (h.ai_provider || 'watsonx').toLowerCase()
          const providerLabel = providerName === 'gemini' ? 'Gemini' : 'watsonx'

          if (!configured) {
            setState({
              status: 'degraded',
              detail: `${h.total_chunks} chunk${h.total_chunks !== 1 ? 's' : ''} · ${providerLabel} not configured`,
              health: h,
            })
          } else {
            setState({
              status: 'connected',
              detail: `${h.total_chunks} chunk${h.total_chunks !== 1 ? 's' : ''} · ${providerLabel} (${h.llm_model})`,
              health: h,
            })
          }
          // Schedule next normal poll
          if (retryTimer.current) clearTimeout(retryTimer.current)
          retryTimer.current = setTimeout(poll, pollIntervalMs)
        })
        .catch(() => {
          if (cancelled) return
          retryCount.current += 1
          setState({ status: 'disconnected', detail: '', health: null })
          scheduleRetry()
        })
    }

    poll()

    return () => {
      cancelled = true
      if (retryTimer.current) clearTimeout(retryTimer.current)
    }
  }, [pollIntervalMs])

  return state
}
