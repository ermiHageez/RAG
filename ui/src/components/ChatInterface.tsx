import { useState, useRef, useEffect, useMemo } from 'react'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import type { ChatMessage } from '../types'
import styles from './ChatInterface.module.css'

interface ChatInterfaceProps {
  messages: ChatMessage[]
  onSend: (message: string) => void
  loading: boolean
  loadingLabel?: string
  showCommandHint?: boolean
  commands?: string[]
}

export default function ChatInterface({ messages, onSend, loading, loadingLabel, showCommandHint, commands = [] }: ChatInterfaceProps) {
  const [input, setInput] = useState('')
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set())
  const [selectedSuggestion, setSelectedSuggestion] = useState(-1)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const suggestions = useMemo(() => {
    if (!input.startsWith('/') || input === '/') return commands
    const partial = input.slice(1).toLowerCase()
    return commands.filter(c => c.toLowerCase().startsWith(partial))
  }, [input, commands])

  const showSuggestions = input.startsWith('/') && suggestions.length > 0

  useEffect(() => {
    setSelectedSuggestion(-1)
  }, [suggestions.length])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed || loading) return
    setInput('')
    setSelectedSuggestion(-1)
    onSend(trimmed)
  }

  const insertCommand = (cmd: string) => {
    setInput('/' + cmd + ' ')
    inputRef.current?.focus()
    setSelectedSuggestion(-1)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (showSuggestions) {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedSuggestion(prev => Math.min(prev + 1, suggestions.length - 1))
        return
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedSuggestion(prev => Math.max(prev - 1, 0))
        return
      }
      if ((e.key === 'Tab' || (e.key === 'Enter' && !e.shiftKey)) && selectedSuggestion >= 0) {
        e.preventDefault()
        insertCommand(suggestions[selectedSuggestion])
        return
      }
      if (e.key === 'Escape') {
        setSelectedSuggestion(-1)
        return
      }
    }

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

  const autoResize = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
  }

  const renderInput = (placeholder: string) => (
    <div className={styles.inputWrapper}>
      {showSuggestions && (
        <div className={styles.suggestions}>
          {suggestions.map((cmd, i) => (
            <div
              key={cmd}
              className={`${styles.suggestion} ${i === selectedSuggestion ? styles.suggestionActive : ''}`}
              onMouseDown={() => insertCommand(cmd)}
            >
              /{cmd}
            </div>
          ))}
        </div>
      )}
      <textarea
        ref={inputRef}
        className={styles.input}
        placeholder={placeholder}
        value={input}
        onChange={autoResize}
        onKeyDown={handleKeyDown}
        rows={1}
      />
      <button className={styles.sendBtn} onClick={handleSend} disabled={!input.trim() || loading}>
        Send
      </button>
    </div>
  )

  if (messages.length === 0 && !loading) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.empty}>
          <SmartToyIcon className={styles.emptyIcon} />
          <div className={styles.emptyTitle}>{showCommandHint ? 'AI Chat with Commands' : 'AI Chat with RAG'}</div>
          <div className={styles.emptyHint}>
            {showCommandHint
              ? 'Type / to see available commands, or just ask a question naturally.'
              : 'Ask questions about Ethiopian companies, tenders, market intelligence, or anything related to eTech\'s business. The AI retrieves relevant context from the knowledge base before answering.'}
          </div>
        </div>
        {renderInput('Ask a question...')}
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
                {loadingLabel && <span className={styles.loadingLabel}>{loadingLabel}</span>}
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {renderInput('Ask a follow-up question...')}
    </div>
  )
}