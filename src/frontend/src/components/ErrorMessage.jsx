/**
 * ErrorMessage — displays a backend or network error in the chat stream.
 *
 * Props:
 *   message  {string}  — user-facing error text (never exposes stack traces or credentials)
 */

function ErrorIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.4" fill="none"/>
      <line x1="7" y1="4.5" x2="7" y2="7.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      <circle cx="7" cy="9.5" r="0.65" fill="currentColor"/>
    </svg>
  )
}

/** Maps technical error strings to friendlier messages */
function friendlyMessage(raw) {
  if (!raw) return 'An unexpected error occurred. Please try again.'
  const lower = raw.toLowerCase()
  if (lower.includes('failed to fetch') || lower.includes('networkerror') || lower.includes('load failed')) {
    return 'Cannot reach the backend. Make sure the server is running on port 8000.'
  }
  if (lower.includes('503') || lower.includes('service unavailable')) {
    return 'The AI service is temporarily unavailable. Check that watsonx credentials are configured.'
  }
  if (lower.includes('502') || lower.includes('bad gateway')) {
    return 'The backend encountered an error communicating with the AI service.'
  }
  if (lower.includes('401') || lower.includes('403') || lower.includes('unauthorized')) {
    return 'Authentication failed. Check the backend configuration.'
  }
  if (lower.includes('404')) {
    return 'The requested resource was not found.'
  }
  // Return the original if it already looks user-friendly (short, no stack trace)
  if (raw.length < 200 && !raw.includes('\n') && !raw.includes('at ')) {
    return raw
  }
  return 'An error occurred while processing your request. Please try again.'
}

export default function ErrorMessage({ message }) {
  return (
    <div className="error-message-row" role="alert">
      <div className="error-bubble">
        <span className="error-icon">
          <ErrorIcon />
        </span>
        <div className="error-content">
          <strong className="error-title">Unable to complete request</strong>
          <span className="error-body">{friendlyMessage(message)}</span>
        </div>
      </div>
    </div>
  )
}
