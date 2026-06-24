import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import RemoveIcon from '@mui/icons-material/Remove'
import type { AnalyticsMetric } from '../types'
import styles from './AnalyticsDashboard.module.css'

interface AnalyticsDashboardProps {
  metrics: AnalyticsMetric[]
  mode: 'sales' | 'marketing' | 'ai'
}

function trendIcon(trend: string) {
  switch (trend) {
    case 'up': return <TrendingUpIcon sx={{ fontSize: 14 }} />
    case 'down': return <TrendingDownIcon sx={{ fontSize: 14 }} />
    default: return <RemoveIcon sx={{ fontSize: 14 }} />
  }
}

function trendClass(trend: string) {
  switch (trend) {
    case 'up': return styles.trendUp
    case 'down': return styles.trendDown
    default: return styles.trendStable
  }
}

export default function AnalyticsDashboard({ metrics, mode }: AnalyticsDashboardProps) {
  if (!metrics || metrics.length === 0) {
    return <div style={{ fontSize: 12, color: '#5f6368', fontStyle: 'italic', padding: '12px 0' }}>
      No analytics data available.
    </div>
  }

  const getBarClass = (index: number) => {
    const classes = [styles.chartBarFill, styles.chartBarFillSecondary, styles.chartBarFillAccent]
    return classes[index % 3]
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.kpiGrid}>
        {metrics.map((metric, i) => (
          <div key={i} className={styles.kpiCard}>
            <div className={styles.kpiLabel}>{metric.label}</div>
            <div className={styles.kpiValue}>
              {metric.value}
              <span className={styles.kpiUnit}>{metric.unit}</span>
            </div>
            <div className={`${styles.kpiTrend} ${trendClass(metric.trend)}`}>
              {trendIcon(metric.trend)}
              {metric.change > 0 ? '+' : ''}{metric.change}% vs last period
            </div>
          </div>
        ))}
      </div>

      <div className={styles.chartSection}>
        <div className={styles.chartHeader}>
          {mode === 'sales' ? 'Performance Overview' : 'Per-Product Performance'}
        </div>
        <div className={styles.chartBody}>
          {metrics.map((metric, i) => (
            <div key={i} className={styles.chartRow}>
              <span className={styles.chartLabel}>{metric.label}</span>
              <div className={styles.chartBar}>
                <div
                  className={`${styles.chartBarFill} ${getBarClass(i)}`}
                  style={{ width: `${Math.min(metric.value, 100)}%` }}
                />
              </div>
              <span className={styles.chartValue}>
                {metric.value}{metric.unit}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
