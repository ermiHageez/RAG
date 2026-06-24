import type { Campaign } from '../types'
import styles from './CampaignTracker.module.css'

interface CampaignTrackerProps {
  campaigns: Campaign[]
  onStatusOverride?: (campaignId: string, newStatus: Campaign['status']) => void
}

const statuses: Campaign['status'][] = ['New', 'Sent', 'Opened', 'Replied', 'Meeting Booked']

const columnClasses: Record<string, string> = {
  'New': styles.columnNew,
  'Sent': styles.columnSent,
  'Opened': styles.columnOpened,
  'Replied': styles.columnReplied,
  'Meeting Booked': styles.columnMeetingBooked,
}

export default function CampaignTracker({ campaigns, onStatusOverride }: CampaignTrackerProps) {
  const getNextStatus = (current: Campaign['status']): Campaign['status'] | null => {
    const idx = statuses.indexOf(current)
    if (idx < statuses.length - 1) return statuses[idx + 1]
    return null
  }

  if (!campaigns || campaigns.length === 0) {
    return <div className={styles.empty}>No campaigns to display.</div>
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.kanban}>
        {statuses.map(status => {
          const campaignsInColumn = campaigns.filter(c => c.status === status)
          return (
            <div key={status} className={`${styles.column} ${columnClasses[status] || ''}`}>
              <div className={styles.columnHeader}>{status}</div>
              <div className={styles.columnCards}>
                {campaignsInColumn.map(campaign => (
                  <div key={campaign.id} className={styles.card}>
                    <div className={styles.cardName}>{campaign.name}</div>
                    <div className={styles.cardStats}>
                      <span className={styles.cardStat}>
                        Leads: <span className={styles.cardStatValue}>{campaign.leads_count}</span>
                      </span>
                      {campaign.opened_count > 0 && (
                        <span className={styles.cardStat}>
                          Opens: <span className={styles.cardStatValue}>{campaign.opened_count}</span>
                        </span>
                      )}
                    </div>
                    {onStatusOverride && getNextStatus(status) && (
                      <button
                        className={styles.overrideBtn}
                        onClick={() => onStatusOverride(campaign.id, getNextStatus(status)!)}
                      >
                        Move to {getNextStatus(status)}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
