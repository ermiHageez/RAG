import CampaignTracker from './CampaignTracker'
import FollowUpScheduler from './FollowUpScheduler'
import type { Campaign, FollowUpRule } from '../types'
import styles from './CampaignLaunchpad.module.css'

interface CampaignLaunchpadProps {
  campaigns: Campaign[]
  followUpRule: FollowUpRule
  onStatusOverride: (campaignId: string, newStatus: Campaign['status']) => void
  onUpdateRule: (rule: FollowUpRule) => void
  onPreview: () => void
}

export default function CampaignLaunchpad({
  campaigns, followUpRule, onStatusOverride, onUpdateRule, onPreview,
}: CampaignLaunchpadProps) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.split}>
        <div className={styles.leftPanel}>
          <section className={styles.section}>
            <div className={styles.sectionTitle}>Campaign Pipeline</div>
            <CampaignTracker campaigns={campaigns} onStatusOverride={onStatusOverride} />
          </section>
        </div>
        <div className={styles.rightPanel}>
          <section className={styles.section}>
            <div className={styles.sectionTitle}>Automation Cadence</div>
            <FollowUpScheduler rule={followUpRule} onUpdateRule={onUpdateRule} />
          </section>
        </div>
      </div>
      <div className={styles.actionBar}>
        <button className={styles.actionBtn} onClick={onPreview}>
          Generate Preview Email
        </button>
      </div>
    </div>
  )
}
