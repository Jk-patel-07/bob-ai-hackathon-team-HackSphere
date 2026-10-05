/**
 * UserMessage — renders a single user turn in the chat.
 * Props:
 *   content  {string}
 */
export default function UserMessage({ content }) {
  return (
    <div className="user-message-row">
      <div className="user-bubble">{content}</div>
    </div>
  )
}
