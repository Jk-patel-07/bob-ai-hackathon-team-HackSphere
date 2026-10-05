import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatPage from './pages/ChatPage'
import KnowledgeBasePage from './pages/KnowledgeBasePage'
import DocumentsPage from './pages/DocumentsPage'
import './styles/global.css'

/**
 * App — top-level shell.
 * Uses simple page-state routing (no external router dependency).
 */
export default function App() {
  const [page, setPage] = useState('chat')    // 'chat' | 'knowledge' | 'documents'
  const [chatKey, setChatKey] = useState(0)   // increment to reset chat

  function handleNewChat() {
    setPage('chat')
    setChatKey((k) => k + 1)
  }

  return (
    <div className="app-shell">
      <Sidebar
        currentPage={page}
        onNavigate={setPage}
        onNewChat={handleNewChat}
      />
      <main className="app-main">
        {page === 'chat' && <ChatPage key={chatKey} />}
        {page === 'knowledge' && <KnowledgeBasePage />}
        {page === 'documents' && <DocumentsPage />}
      </main>
    </div>
  )
}
