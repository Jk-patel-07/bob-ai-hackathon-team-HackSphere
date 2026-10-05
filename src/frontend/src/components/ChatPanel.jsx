import { useEffect, useRef, useState } from 'react'
import { search } from '../api'
import AssistantMessage from './AssistantMessage'

/**
 * ChatPanel — the main conversation area.
 * Props:
 *   categoryFilter {string|null} — optional category selected from sidebar
 */
export default function ChatPanel({ categoryFilter }) {
  const [messages, setMessages] = useState([])  // { role: 'user'|'assistant'|'error', content }
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  // Auto-scroll to bottom whenever messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend(e) {
    e.preventDefault()
    const q = input.trim()
    if (!q || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: q }])
    setInput('')
    setLoading(true)

    try {
      const result = await search(q, categoryFilter ?? null)
      setMessages((prev) => [...prev, { role: 'assistant', content: result }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'error', content: err.message ?? 'An unexpected error occurred.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSend(e)
    }
  }

  return (
    <div className="chat-panel">
      {/* Message list */}
      <div className="messages-area">
        {messages.length === 0 && !loading && (
          <div className="empty-state">
            <div className="empty-state-icon">⬡</div>
            <p className="empty-state-title">Ask a chip design question</p>
            <p className="empty-state-hint">
              Query PDK rules, DRC constraints, timing parameters, SPICE models,
              latch-up guidelines, and more.
            </p>
          </div>
        )}

        {messages.map((msg, i) => {
          if (msg.role === 'user') {
            return (
              <div key={i} className="user-message-row">
                <div className="user-bubble">{msg.content}</div>
              </div>
            )
          }
          if (msg.role === 'error') {
            return (
              <div key={i} className="error-message-row">
                <div className="error-bubble">
                  <strong>Error</strong> — {msg.content}
                </div>
              </div>
            )
          }
          return (
            <div key={i} className="assistant-row">
              <AssistantMessage result={msg.content} />
            </div>
          )
        })}

        {loading && (
          <div className="assistant-row">
            <div className="loading-bubble">
              <span className="loading-dots">
                <span /><span /><span />
              </span>
              Searching knowledge base…
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <form className="input-bar" onSubmit={handleSend}>
        {categoryFilter && (
          <span className="filter-badge">Filter: {categoryFilter}</span>
        )}
        <textarea
          className="query-input"
          placeholder="Ask a chip design question…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={loading}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={loading || !input.trim()}
          aria-label="Send"
        >
          Send
        </button>
      </form>
    </div>
  )
}
