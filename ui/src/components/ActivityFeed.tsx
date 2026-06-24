import TimelineIcon from '@mui/icons-material/Timeline'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import EditIcon from '@mui/icons-material/Edit'
import type { ActivityEntry } from '../types'
import styles from './ActivityFeed.module.css'

interface ActivityFeedProps {
  activities: ActivityEntry[]
}

function activityIcon(type: string) {
  switch (type) {
    case 'ai_suggestion': return <SmartToyIcon sx={{ fontSize: 14, color: '#2979ff' }} />
    case 'human_approval': return <CheckCircleIcon sx={{ fontSize: 14, color: '#00c853' }} />
    case 'human_rejection': return <CancelIcon sx={{ fontSize: 14, color: '#ff1744' }} />
    case 'human_edit': return <EditIcon sx={{ fontSize: 14, color: '#2979ff' }} />
    default: return <TimelineIcon sx={{ fontSize: 14, color: '#5f6368' }} />
  }
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const sec = Math.floor(diff / 1000)
  if (sec < 5) return 'just now'
  if (sec < 60) return `${sec}s ago`
  const min = Math.floor(sec / 60)
  if (min < 60) return `${min}m ago`
  return `${Math.floor(min / 60)}h ago`
}

export default function ActivityFeed({ activities }: ActivityFeedProps) {
  if (activities.length === 0) return null

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <TimelineIcon sx={{ fontSize: 16 }} />
        Activity Log
      </div>
      <div className={styles.list}>
        {activities.map(act => (
          <div key={act.id} className={styles.item}>
            <div className={styles.itemIcon}>
              {activityIcon(act.type)}
            </div>
            <div className={styles.itemBody}>
              <div className={styles.itemMessage}>{act.message}</div>
              <div className={styles.itemMeta}>
                <span className={styles.itemStep}>{act.step}</span>
                <span className={styles.itemTime}>{timeAgo(act.timestamp)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
