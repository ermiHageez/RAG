import { useState } from 'react'
import type { FollowUpRule } from '../types'
import styles from './FollowUpScheduler.module.css'

interface FollowUpSchedulerProps {
  rule: FollowUpRule
  onUpdateRule: (rule: FollowUpRule) => void
}

export default function FollowUpScheduler({ rule, onUpdateRule }: FollowUpSchedulerProps) {
  const [localRule, setLocalRule] = useState(rule)

  const removeExclusion = (lead: string) => {
    const updated = {
      ...localRule,
      excluded_leads: localRule.excluded_leads.filter(l => l !== lead),
    }
    setLocalRule(updated)
    onUpdateRule(updated)
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.rules}>
        <div className={styles.ruleCard}>
          <span className={styles.ruleLabel}>Initial Delay</span>
          <span className={styles.ruleValue}>{localRule.initial_delay_days}</span>
          <span className={styles.ruleUnit}>days before first follow-up</span>
        </div>
        <div className={styles.ruleCard}>
          <span className={styles.ruleLabel}>Loop Cycle</span>
          <span className={styles.ruleValue}>{localRule.loop_cycle_days}</span>
          <span className={styles.ruleUnit}>days between follow-ups</span>
        </div>
        <div className={styles.ruleCard}>
          <span className={styles.ruleLabel}>Max Follow-ups</span>
          <span className={styles.ruleValue}>{localRule.max_follow_ups}</span>
          <span className={styles.ruleUnit}>maximum attempts per lead</span>
        </div>
      </div>

      <div className={styles.exclusions}>
        <div className={styles.exclusionsHeader}>
          Excluded Leads
          <span className={styles.exclusionsCount}>{localRule.excluded_leads.length} leads</span>
        </div>
        <div className={styles.exclusionsList}>
          {localRule.excluded_leads.length === 0 ? (
            <span style={{ fontSize: 11, color: '#5f6368', padding: '4px 8px' }}>
              No leads excluded
            </span>
          ) : (
            localRule.excluded_leads.map(lead => (
              <span key={lead} className={styles.exclusionTag}>
                {lead}
                <span className={styles.exclusionRemove} onClick={() => removeExclusion(lead)}>×</span>
              </span>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
