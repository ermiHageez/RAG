import { useState, useRef, useEffect } from 'react'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import type { ChatMessage } from '../types'
import styles from './ChatInterface.module.css'

interface ChatInterfaceProps {
  messages: ChatMessage[]
  onSend: (message: string) => void
  loading: boolean
  showCommandHint?: boolean
}

export default function ChatInterface({ messages, onSend, loading, showCommandHint }: ChatInterfaceProps) {
  const [input, setInput] = useState('')
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set())
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed || loading) return
    setInput('')
    onSend(trimmed)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const toggleSources = (id: string) => {
    setExpandedSources(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const formatTime = (ts: string) => {
    try {
      return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch {
      return ''
    }
  }

  if (messages.length === 0 && !loading) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.empty}>
          <SmartToyIcon className={styles.emptyIcon} />
          <div className={styles.emptyTitle}>{showCommandHint ? 'AI Chat with Commands' : 'AI Chat with RAG'}</div>
          <div className={styles.emptyHint}>
            {showCommandHint
              ? 'Type /help to see all available commands, or just ask a question naturally.'
              : 'Ask questions about Ethiopian companies, tenders, market intelligence, or anything related to eTech\'s business. The AI retrieves relevant context from the knowledge base before answering.'}
          </div>
        </div>
        <div className={styles.inputRow}>
          <input
            className={styles.input}
            placeholder="Ask a question..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button className={styles.sendBtn} onClick={handleSend} disabled={!input.trim() || loading}>
            Send
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.messages}>
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`${styles.message} ${msg.role === 'user' ? styles.messageUser : styles.messageAssistant}`}
          >
            <div className={`${styles.bubble} ${msg.role === 'user' ? styles.bubbleUser : styles.bubbleAssistant}`}>
              {msg.content}
            </div>

            {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
              <>
                <button
                  className={styles.sourcesToggle}
                  onClick={() => toggleSources(msg.id)}
                >
                  {expandedSources.has(msg.id) ? 'Hide' : 'Show'} sources ({msg.sources.length})
                </button>
                {expandedSources.has(msg.id) && (
                  <div className={styles.sourcesList}>
                    {msg.sources.map((src, i) => (
                      <div key={i} className={styles.sourceItem}>
                        <div className={styles.sourceTitle}>
                          {src.url ? (
                            <a href={src.url} target="_blank" rel="noopener noreferrer" style={{ color: '#00c853', textDecoration: 'underline' }}>
                              {src.title || `Source ${i + 1}`}
                            </a>
                          ) : (
                            src.title || `Source ${i + 1}`
                          )}
                        </div>
                        <div className={styles.sourceSnippet}>{src.snippet}</div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}

            <div className={styles.timestamp}>{formatTime(msg.timestamp)}</div>
          </div>
        ))}

        {loading && (
          <div className={`${styles.message} ${styles.messageAssistant}`}>
            <div className={`${styles.bubble} ${styles.bubbleAssistant}`}>
              <div className={styles.loading}>
                <span className={styles.dot} />
                <span className={styles.dot} />
                <span className={styles.dot} />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className={styles.inputRow}>
        <input
          className={styles.input}
          placeholder="Ask a follow-up question..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className={styles.sendBtn} onClick={handleSend} disabled={!input.trim() || loading}>
          Send
        </button>
      </div>
    </div>
  )
}
