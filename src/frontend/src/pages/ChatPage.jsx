/**
 * ChatPage — main conversation page.
 *
 * Welcome state → clickable example cards → message list → input bar.
 * No AI answers are hardcoded. No credentials in this file.
 */
import { useEffect, useRef, useState } from 'react'
import { getCategories, searchKnowledge } from '../services/api'
import UserMessage from '../components/UserMessage'
import AssistantMessage from '../components/AssistantMessage'
import LoadingMessage from '../components/LoadingMessage'
import ErrorMessage from '../components/ErrorMessage'

/* Example questions — question text + category label */
const EXAMPLES = [
  { question: 'What is the minimum poly gate overhang?',      label: 'DRC Rule' },
  { question: 'What are the latch-up prevention requirements?', label: 'Design Guideline' },
  { question: 'What design-rule information is available?',    label: 'Knowledge Search' },
]

function WelcomeChipIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <rect x="7" y="7" width="14" height="14" rx="2" stroke="currentColor" strokeWidth="1.8" fill="none"/>
      <line x1="10" y1="7" x2="10" y2="4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="14" y1="7" x2="14" y2="4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="18" y1="7" x2="18" y2="4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="10" y1="21" x2="10" y2="24" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="14" y1="21" x2="14" y2="24" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="18" y1="21" x2="18" y2="24" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="7" y1="10" x2="4" y2="10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="7" y1="14" x2="4" y2="14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="7" y1="18" x2="4" y2="18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="21" y1="10" x2="24" y2="10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="21" y1="14" x2="24" y2="14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <line x1="21" y1="18" x2="24" y2="18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <rect x="10" y="10" width="8" height="8" rx="1" fill="currentColor" opacity="0.2"/>
    </svg>
  )
}

function CardArrowIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M3 7h8M8 4l3 3-3 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M8 13V3M3 8l5-5 5 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [categoriesList, setCategoriesList] = useState(['PDK', 'DRC', 'Design Guidelines', 'Application Notes', 'SPICE Models'])
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    getCategories()
      .then((res) => {
        if (res.categories && res.categories.length > 0) {
          const names = res.categories.map((c) => c.name)
          setCategoriesList(Array.from(new Set(['PDK', 'DRC', 'Design Guidelines', 'Application Notes', 'SPICE Models', ...names])))
        }
      })
      .catch(() => {})
  }, [])

  // Auto-scroll to newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Auto-resize textarea (max ~5 lines)
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 140)}px`
  }, [input])

  async function sendMessage(query) {
    const q = query.trim()
    if (!q || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: q }])
    setInput('')
    setLoading(true)

    const catParam = selectedCategory === 'All' ? null : selectedCategory

    try {
      const result = await searchKnowledge(q, catParam)
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

  function handleSubmit(e) {
    e.preventDefault()
    sendMessage(input)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  function handleExampleClick(question) {
    // Send immediately via the real search flow — same path as manual input.
    sendMessage(question)
  }

  const isEmpty = messages.length === 0 && !loading

  return (
    <div className="chat-page">
      {/* Page header */}
      <div className="chat-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="chat-header-title">Chip Design Knowledge Assistant</h1>
          <p className="chat-header-subtitle">
            Grounded answers from your semiconductor design knowledge
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label htmlFor="chat-category-select" className="form-label" style={{ margin: 0, fontSize: '11px' }}>
            Filter:
          </label>
          <select
            id="chat-category-select"
            className="form-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{ padding: '4px 8px', fontSize: '12px' }}
          >
            <option value="All">All Knowledge</option>
            {categoriesList.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Message area */}
      <div className="messages-area" role="log" aria-live="polite" aria-label="Conversation">
        {isEmpty && (
          <div className="welcome-state">
            <div className="welcome-icon">
              <WelcomeChipIcon />
            </div>
            <h2 className="welcome-title">How can I help with your chip design?</h2>
            <p className="welcome-hint">
              Ask questions about PDKs, DRC rules, design guidelines,
              application notes, and other approved engineering knowledge.
            </p>
            <div className="example-cards" role="list" aria-label="Example questions">
              {EXAMPLES.map(({ question, label }) => (
                <button
                  key={question}
                  className="example-card"
                  onClick={() => handleExampleClick(question)}
                  aria-label={`Ask: ${question}`}
                  role="listitem"
                >
                  <span className="example-card-icon">
                    <CardArrowIcon />
                  </span>
                  <span className="example-card-body">
                    <span className="example-card-question">{question}</span>
                    <span className="example-card-label">{label}</span>
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => {
          if (msg.role === 'user') {
            return <UserMessage key={i} content={msg.content} />
          }
          if (msg.role === 'error') {
            return <ErrorMessage key={i} message={msg.content} />
          }
          return (
            <div key={i} className="assistant-row">
              <AssistantMessage result={msg.content} />
            </div>
          )
        })}

        {loading && <LoadingMessage />}

        <div ref={bottomRef} aria-hidden="true" />
      </div>

      {/* Input bar */}
      <div className="input-bar">
        <form className="input-form" onSubmit={handleSubmit}>
          <label htmlFor="chat-input" className="sr-only">
            Ask a chip design question
          </label>
          <textarea
            id="chat-input"
            ref={textareaRef}
            className="chat-input"
            placeholder="Ask about PDKs, DRC rules, design guidelines…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={loading}
            aria-label="Chat input"
          />
          <button
            type="submit"
            className="send-btn"
            disabled={loading || !input.trim()}
            aria-label="Send message"
          >
            <span className="send-icon">
              <SendIcon />
            </span>
          </button>
        </form>
        <div className="input-footer">
          <span className="input-hint">Enter to send · Shift+Enter for new line</span>
          <span className="input-ground-note">Answers are grounded in available knowledge-base documents</span>
        </div>
      </div>
    </div>
  )
}
