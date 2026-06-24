import { useState } from 'react'
import EmailIcon from '@mui/icons-material/Email'
import DownloadIcon from '@mui/icons-material/Download'
import SendIcon from '@mui/icons-material/Send'
import type { EmailDraft } from '../types'
import styles from './EmailEditor.module.css'

interface EmailEditorProps {
  draft: EmailDraft
  onEdit: (subject: string, body: string) => void
  onRegenerate: () => void
  onDownload?: () => void
  onTestSend?: () => void
  mode: 'sales' | 'marketing'
}

export default function EmailEditor({ draft, onEdit, onRegenerate, onDownload, onTestSend, mode }: EmailEditorProps) {
  const [subject, setSubject] = useState(draft?.subject || '')
  const [body, setBody] = useState(draft?.email_body || '')

  if (!draft) {
    return <div className={styles.empty}>No email draft generated.</div>
  }

  const score = draft.personalization_score ?? 0
  const gaugeClass = score >= 0.7 ? styles.gaugeFillGood : score >= 0.3 ? styles.gaugeFillWarn : styles.gaugeFillBad
  const gaugeWidth = `${Math.round(score * 100)}%`

  return (
    <div className={styles.wrapper}>
      <div className={styles.infoRow}>
        <span className={styles.infoChip}>
          <EmailIcon sx={{ fontSize: 12 }} />
          To: {draft.lead_name || 'Unknown'}
        </span>
        {draft.validated_email && (
          <span className={styles.infoChip} style={{ borderColor: 'rgba(41,121,255,0.3)', color: '#2979ff' }}>
            {draft.validated_email}
          </span>
        )}
      </div>

      <div className={styles.gauge}>
        <span className={styles.gaugeLabel}>
          Personalization Score: <span className={styles.gaugeValue}>{score.toFixed(2)}</span>
        </span>
        <div className={styles.gaugeBar}>
          <div className={`${styles.gaugeFill} ${gaugeClass}`} style={{ width: gaugeWidth }} />
        </div>
      </div>

      <div className={styles.field}>
        <label className={styles.fieldLabel}>Subject</label>
        <input
          className={styles.fieldInput}
          value={subject}
          onChange={e => setSubject(e.target.value)}
        />
      </div>

      <div className={styles.field}>
        <label className={styles.fieldLabel}>Email Body</label>
        <textarea
          className={styles.fieldTextarea}
          value={body}
          onChange={e => setBody(e.target.value)}
          rows={8}
        />
      </div>

      <div className={styles.actions}>
        <button
          className={`${styles.btn} ${styles.btnPrimary}`}
          onClick={() => onEdit(subject, body)}
          disabled={!subject.trim() || !body.trim()}
        >
          <EmailIcon sx={{ fontSize: 14 }} />
          Approve with edits
        </button>
        <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={onRegenerate}>
          Regenerate
        </button>
        {mode === 'marketing' && onTestSend && (
          <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={onTestSend}>
            <SendIcon sx={{ fontSize: 14 }} />
            Send Test Email to Me
          </button>
        )}
        {mode === 'sales' && onDownload && (
          <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={onDownload}>
            <DownloadIcon sx={{ fontSize: 14 }} />
            Download HTML
          </button>
        )}
      </div>

      {score < 0.5 && (
        <div className={styles.lowScoreWarning}>
          Personalization score is low. Consider adding specific details about this prospect's sector,
          their needs, or referencing a mutual connection to improve engagement.
        </div>
      )}
    </div>
  )
}
