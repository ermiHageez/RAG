import { useState } from 'react'
import SecurityIcon from '@mui/icons-material/Security'
import SendIcon from '@mui/icons-material/Send'
import styles from './QueryInput.module.css'

interface QueryInputProps {
  onsubmit: (query: string) => void
  disabled: boolean
  querySubmitted: string
  mode: 'sales' | 'marketing' | 'ai'
}

export default function QueryInput({ onsubmit, disabled, querySubmitted, mode }: QueryInputProps) {
  const [query, setQuery] = useState('')
  const [showSecurity, setShowSecurity] = useState(false)

  const handleSubmit = () => {
    if (!query.trim() || disabled) return
    onsubmit(query.trim())
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  if (querySubmitted) {
    return (
      <div className={`${styles.wrapper}`}>
        <div className={styles.queryDisplay}>
          <div className={styles.queryLabel}>Active Query</div>
          <div className={styles.queryValue}>{querySubmitted}</div>
        </div>
      </div>
    )
  }

  const placeholder = mode === 'sales'
    ? 'e.g. Find banking leads and security tenders in Ethiopia'
    : 'e.g. Create an outreach campaign for eTech cloud hosting'

  return (
    <div className={styles.wrapper}>
      <div className={styles.panel}>
        <div className={styles.title}>
          <SendIcon sx={{ color: '#00c853', fontSize: 16 }} />
          What can the co-pilot help you with?
        </div>
        <div className={styles.inputRow}>
          <textarea
            className={styles.textField}
            rows={2}
            placeholder={placeholder}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            maxLength={2000}
          />
          <button
            className={styles.submitBtn}
            onClick={handleSubmit}
            disabled={disabled || !query.trim()}
          >
            {disabled ? 'Processing...' : 'Go'}
          </button>
        </div>
        <div className={styles.security}>
          <SecurityIcon sx={{ fontSize: 12, color: '#5f6368' }} />
          <span
            className={styles.securityText}
            onClick={() => setShowSecurity(v => !v)}
          >
            Your input is sanitized for security
          </span>
        </div>
        {showSecurity && (
          <div className={styles.securityDetail}>
            Your input is scanned for prompt injection patterns. Queries are capped at 2,000 characters
            and control characters are stripped. This protects the AI from malicious instructions.
          </div>
        )}
      </div>
    </div>
  )
}
