import { useState } from 'react'
import type { CampaignTemplate } from '../types'
import styles from './CampaignTemplateEngine.module.css'

interface CampaignTemplateEngineProps {
  templates: CampaignTemplate[]
  onSelect: (template: CampaignTemplate) => void
}

export default function CampaignTemplateEngine({ templates, onSelect }: CampaignTemplateEngineProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null)

  if (!templates || templates.length === 0) {
    return <div className={styles.empty}>No templates available.</div>
  }

  const handleSelect = (tpl: CampaignTemplate) => {
    setSelectedId(tpl.id)
    onSelect(tpl)
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.grid}>
        {templates.map(tpl => (
          <div
            key={tpl.id}
            className={`${styles.card} ${selectedId === tpl.id ? styles.cardSelected : ''}`}
            onClick={() => handleSelect(tpl)}
          >
            <span className={styles.cardLayout}>{tpl.layout}</span>
            <div className={styles.cardName}>{tpl.name}</div>
            <div className={styles.cardDesc}>{tpl.description}</div>
            <div className={styles.cardCategories}>
              {tpl.target_categories.map(cat => (
                <span key={cat} className={styles.cardCategory}>{cat}</span>
              ))}
            </div>
            <div className={styles.cardEffectiveness}>
              {(tpl.historical_effectiveness * 100).toFixed(0)}% historical effectiveness
            </div>
            {selectedId === tpl.id && (
              <button className={styles.selectBtn}>Selected</button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
