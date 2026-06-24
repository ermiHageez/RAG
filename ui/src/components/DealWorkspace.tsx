import LeadReview from './LeadReview'
import TenderReview from './TenderReview'
import IntelReview from './IntelReview'
import EmailEditor from './EmailEditor'
import type { Lead, Tender, SalesIntel, EmailDraft } from '../types'
import styles from './DealWorkspace.module.css'

interface DealWorkspaceProps {
  leads: Lead[]
  tenders: Tender[]
  intel: SalesIntel | null
  emailDraft: EmailDraft | null
  onApprove: () => void
  onEmailEdit: (subject: string, body: string) => void
  onRegenerate: () => void
  onNotesChange: (notes: string) => void
}

export default function DealWorkspace({
  leads, tenders, intel, emailDraft,
  onApprove, onEmailEdit, onRegenerate, onNotesChange,
}: DealWorkspaceProps) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.grid}>
        <div className={styles.leftPanel}>
          <section className={styles.section}>
            <div className={styles.sectionTitle}>Lead Details</div>
            <LeadReview leads={leads} onApprove={() => {}} />
          </section>
          <section className={styles.section}>
            <div className={styles.sectionTitle}>Matching Tenders</div>
            <TenderReview tenders={tenders} onApprove={() => {}} />
          </section>
        </div>
        <div className={styles.centerPanel}>
          <section className={styles.section}>
            <div className={styles.sectionTitle}>Market Intelligence</div>
            <IntelReview intel={intel || { summary: '', insights: [], total_leads: leads.length, total_tenders: tenders.length, cross_referenced_sources: [] }} onNotesChange={onNotesChange} />
          </section>
        </div>
        <div className={styles.rightPanel}>
          <section className={styles.section}>
            <div className={styles.sectionTitle}>Email Draft</div>
            {emailDraft ? (
              <EmailEditor
                draft={emailDraft}
                onEdit={onEmailEdit}
                onRegenerate={onRegenerate}
                mode="sales"
              />
            ) : (
              <div style={{ padding: 16, color: '#5f6368', fontSize: 13, fontStyle: 'italic' }}>
                No email draft generated yet.
              </div>
            )}
          </section>
        </div>
      </div>
      <div className={styles.actionBar}>
        <button className={styles.actionBtn} onClick={onApprove}>
          Approve & Send to Prospect
        </button>
      </div>
    </div>
  )
}
