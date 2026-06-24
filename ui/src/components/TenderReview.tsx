import { useState } from 'react'
import AssignmentIcon from '@mui/icons-material/Assignment'
import type { Tender } from '../types'
import styles from './TenderReview.module.css'

interface TenderReviewProps {
  tenders: Tender[]
  onApprove: () => void
}

export default function TenderReview({ tenders, onApprove }: TenderReviewProps) {
  const [localTenders, setLocalTenders] = useState(tenders)

  const moveUp = (index: number) => {
    if (index === 0) return
    setLocalTenders(prev => {
      const next = [...prev]
      ;[next[index - 1], next[index]] = [next[index], next[index - 1]]
      return next
    })
  }

  const moveDown = (index: number) => {
    if (index === localTenders.length - 1) return
    setLocalTenders(prev => {
      const next = [...prev]
      ;[next[index], next[index + 1]] = [next[index + 1], next[index]]
      return next
    })
  }

  const urgencyClass = (urgency: string) => {
    switch (urgency) {
      case 'red': return styles.urgencyRed
      case 'amber': return styles.urgencyAmber
      case 'green': return styles.urgencyGreen
      default: return ''
    }
  }

  if (!localTenders || localTenders.length === 0) {
    return <div className={styles.empty}>No tenders found.</div>
  }

  return (
    <div className={styles.wrapper}>
      {localTenders.map((tender, i) => (
        <div key={tender.id} className={styles.card}>
          <div className={styles.cardBody}>
            <div className={styles.title}>
              <AssignmentIcon sx={{ fontSize: 13, color: '#2979ff' }} />
              {tender.title}
            </div>
            <div className={styles.category}>
              {tender.category} · {tender.source}
            </div>
            {tender.description && (
              <div className={styles.description}>{tender.description}</div>
            )}
            {tender.deadline && (
              <div className={styles.deadline}>Deadline: {tender.deadline} ({tender.days_remaining} days remaining)</div>
            )}
            <div className={styles.orderBtns}>
              <button className={styles.orderBtn} onClick={() => moveUp(i)} disabled={i === 0}>↑</button>
              <button className={styles.orderBtn} onClick={() => moveDown(i)} disabled={i === localTenders.length - 1}>↓</button>
            </div>
          </div>
          <div className={styles.meta}>
            <div className={`${styles.score} ${
              tender.relevance_score >= 0.7 ? styles.scoreHigh
              : tender.relevance_score >= 0.4 ? styles.scoreMid
              : styles.scoreLow
            }`}>
              {tender.relevance_score.toFixed(2)}
            </div>
            <div className={`${styles.urgencyBadge} ${urgencyClass(tender.urgency)}`}>
              {tender.urgency}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
