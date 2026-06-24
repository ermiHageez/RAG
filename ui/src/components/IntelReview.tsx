import { useState } from 'react'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import type { SalesIntel } from '../types'
import styles from './IntelReview.module.css'

interface IntelReviewProps {
  intel: SalesIntel
  onNotesChange: (notes: string) => void
}

export default function IntelReview({ intel, onNotesChange }: IntelReviewProps) {
  const [selectedSource, setSelectedSource] = useState<string | null>(null)

  if (!intel || !intel.summary) {
    return <div className={styles.wrapper}>
      <div className={styles.summaryBox}>
        <div style={{ fontSize: 12, color: '#5f6368', fontStyle: 'italic' }}>
          No sales intelligence data available.
        </div>
      </div>
      <div className={styles.dualPanel}>
        <div className={styles.notesPanel}>
          <div className={styles.notesHeader}>Field Notes</div>
          <textarea
            className={styles.notesArea}
            placeholder="Add your own insights, notes, or corrections here..."
            onChange={e => onNotesChange(e.target.value)}
          />
          <div className={styles.notesHint}>Your notes will be included in the final report.</div>
        </div>
      </div>
    </div>
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.summaryBox}>
        <div className={styles.stats}>
          <span className={styles.stat}>
            <AnalyticsIcon sx={{ fontSize: 13 }} />
            Leads: <span className={styles.statValue}>{intel.total_leads}</span>
          </span>
          <span className={styles.stat}>
            Tenders: <span className={styles.statValue}>{intel.total_tenders}</span>
          </span>
        </div>
        <div className={styles.summaryText}>{intel.summary}</div>
      </div>

      <div className={styles.dualPanel}>
        <div className={styles.sourcePanel}>
          <div className={styles.sourceHeader}>
            Cross-Referenced Sources ({intel.cross_referenced_sources?.length || 0})
          </div>
          <div className={styles.sourceList}>
            {(intel.cross_referenced_sources || []).map(src => (
              <div
                key={src.id}
                className={styles.sourceItem}
                onClick={() => setSelectedSource(selectedSource === src.id ? null : src.id)}
              >
                <div className={styles.sourceItemTitle}>{src.title}</div>
                <div className={styles.sourceItemSnippet}>{src.snippet}</div>
                <div className={styles.sourceItemSource}>{src.source}</div>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.notesPanel}>
          <div className={styles.notesHeader}>Field Notes</div>
          <textarea
            className={styles.notesArea}
            placeholder="Add your own insights, notes, or corrections here..."
            onChange={e => onNotesChange(e.target.value)}
          />
          <div className={styles.notesHint}>Your notes will be included in the final report.</div>
        </div>
      </div>
    </div>
  )
}
