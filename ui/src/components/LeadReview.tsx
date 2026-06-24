import { useState } from 'react'
import BusinessIcon from '@mui/icons-material/Business'
import type { Lead } from '../types'
import styles from './LeadReview.module.css'

interface LeadReviewProps {
  leads: Lead[]
  onApprove: () => void
}

export default function LeadReview({ leads, onApprove }: LeadReviewProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set(leads.map(l => l.id)))
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editValue, setEditValue] = useState('')
  const [localLeads, setLocalLeads] = useState(leads)
  const [newLeadName, setNewLeadName] = useState('')

  const toggleSelect = (id: string) => {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const startEdit = (lead: Lead) => {
    setEditingId(lead.id)
    setEditValue(lead.company_name)
  }

  const saveEdit = (id: string) => {
    setLocalLeads(prev => prev.map(l => l.id === id ? { ...l, company_name: editValue } : l))
    setEditingId(null)
  }

  const addLead = () => {
    if (!newLeadName.trim()) return
    const newLead: Lead = {
      id: `manual_${Date.now()}`,
      company_name: newLeadName.trim(),
      sector: 'Manual Entry',
      location: 'Unknown',
      contact: '',
      description: 'Manually added lead',
      source: 'Manual Input',
      qualification_score: 0.5,
    }
    setLocalLeads(prev => [...prev, newLead])
    setSelected(prev => new Set(prev).add(newLead.id))
    setNewLeadName('')
  }

  if (!localLeads || localLeads.length === 0) {
    return <div className={styles.empty}>No leads found.</div>
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.addLeadForm}>
        <input
          className={styles.addLeadInput}
          placeholder="Add a lead manually..."
          value={newLeadName}
          onChange={e => setNewLeadName(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addLead()}
        />
        <button className={styles.addLeadBtn} onClick={addLead}>Add</button>
      </div>

      {localLeads.map(lead => (
        <div key={lead.id} className={`${styles.card} ${selected.has(lead.id) ? styles.cardSelected : ''}`}>
          <label className={styles.checkbox}>
            <input
              type="checkbox"
              checked={selected.has(lead.id)}
              onChange={() => toggleSelect(lead.id)}
              style={{ accentColor: '#00c853' }}
            />
          </label>
          <div className={styles.cardBody}>
            {editingId === lead.id ? (
              <input
                className={styles.companyNameInput}
                value={editValue}
                onChange={e => setEditValue(e.target.value)}
                onBlur={() => saveEdit(lead.id)}
                onKeyDown={e => e.key === 'Enter' && saveEdit(lead.id)}
                autoFocus
              />
            ) : (
              <div className={styles.companyName} onClick={() => startEdit(lead)}>
                <BusinessIcon sx={{ fontSize: 13, color: '#00c853' }} />
                {lead.company_name}
              </div>
            )}
            <div className={styles.metadata}>
              <span>{lead.sector}</span>
              <span>·</span>
              <span>{lead.location}</span>
            </div>
            {lead.description && (
              <div className={styles.description}>{lead.description}</div>
            )}
            {lead.contact && (
              <div className={styles.contact}>Contact: {lead.contact}</div>
            )}
            <div className={styles.source}>
              <span className={styles.sourceTag}>{lead.source}</span>
            </div>
          </div>
          <div className={`${styles.score} ${
            lead.qualification_score >= 0.7 ? styles.scoreHigh
            : lead.qualification_score >= 0.4 ? styles.scoreMid
            : styles.scoreLow
          }`}>
            {lead.qualification_score.toFixed(1)}
          </div>
        </div>
      ))}
    </div>
  )
}
