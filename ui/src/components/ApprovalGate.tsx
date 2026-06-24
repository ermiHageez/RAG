import { useState } from 'react'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined'
import SaveAltIcon from '@mui/icons-material/SaveAlt'
import styles from './ApprovalGate.module.css'

interface ApprovalGateProps {
  leadCount: number
  tenderCount: number
  hasDraft: boolean
  onApprove: () => void
  onReject: () => void
  onSave: () => void
}

export default function ApprovalGate({
  leadCount, tenderCount, hasDraft,
  onApprove, onReject, onSave,
}: ApprovalGateProps) {
  const [scheduleNote, setScheduleNote] = useState('')
  const [scheduleDate, setScheduleDate] = useState('')
  const [scheduleTime, setScheduleTime] = useState('')

  return (
    <div className={styles.wrapper}>
      <div className={styles.summary}>
        <span className={`${styles.summaryChip} ${leadCount > 0 ? styles.summaryChipGood : ''}`}>
          {leadCount} leads
        </span>
        <span className={`${styles.summaryChip} ${tenderCount > 0 ? styles.summaryChipGood : ''}`}>
          {tenderCount} tenders
        </span>
        <span className={`${styles.summaryChip} ${hasDraft ? styles.summaryChipGood : styles.summaryChipWarn}`}>
          {hasDraft ? 'Email drafted' : 'No email'}
        </span>
      </div>

      <hr className={styles.divider} />

      <div className={styles.field}>
        <label className={styles.fieldLabel}>Schedule Send</label>
        <div className={styles.scheduler}>
          <input
            className={styles.schedulerInput}
            type="date"
            value={scheduleDate}
            onChange={e => setScheduleDate(e.target.value)}
          />
          <input
            className={styles.schedulerInput}
            type="time"
            value={scheduleTime}
            onChange={e => setScheduleTime(e.target.value)}
          />
        </div>
      </div>

      <div className={styles.field}>
        <label className={styles.fieldLabel}>Note to team</label>
        <textarea
          className={styles.fieldInput}
          rows={2}
          placeholder="Add a note to the team about this send..."
          value={scheduleNote}
          onChange={e => setScheduleNote(e.target.value)}
        />
      </div>

      <div className={styles.actions}>
        <button className={`${styles.btn} ${styles.btnApprove}`} onClick={onApprove}>
          <CheckCircleOutlineIcon sx={{ fontSize: 16 }} />
          Approve & Send
        </button>
        <button className={`${styles.btn} ${styles.btnReject}`} onClick={onReject}>
          <CancelOutlinedIcon sx={{ fontSize: 16 }} />
          Reject
        </button>
        <button className={`${styles.btn} ${styles.btnSave}`} onClick={onSave}>
          <SaveAltIcon sx={{ fontSize: 16 }} />
          Save as Draft
        </button>
      </div>
    </div>
  )
}
