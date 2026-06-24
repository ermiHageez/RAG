import axios from 'axios'
import type { CampaignTemplate, Campaign, FollowUpRule, AnalyticsMetric } from '../types'

const api = axios.create({
  baseURL: '/',
  timeout: 30000,
})

interface BackendTemplateEntry {
  product: string
  filename: string
  exists: boolean
}

interface BackendCampaignStats {
  total: number
  by_status: Record<string, number>
  by_product: Record<string, number>
  conversion_rate: number
}

interface BackendFollowUpConfig {
  enabled: boolean
  initial_delay_days: number
  max_follow_ups: number
  cadence_days: number
}

interface BackendAnalyticsSummary {
  total_leads: number
  emails_sent: number
  emails_opened: number
  replies: number
  meetings_booked: number
  open_rate: number
  reply_rate: number
  conversion_rate: number
}

const LAYOUT_MAP: Record<string, string> = {
  Ehealth: 'hero-card',
  ERP: 'editorial',
  SCCO: 'event-banner',
  eShare: 'story-card',
  General: 'editorial',
}

const TEMPLATE_DESCRIPTIONS: Record<string, string> = {
  Ehealth: 'Healthcare-focused template with compliance badges and trust signals.',
  ERP: 'Enterprise-grade layout featuring integration diagrams and ROI calculators.',
  SCCO: 'Security-focused template with certification highlights and threat analysis.',
  eShare: 'Collaboration template with team features and workflow showcases.',
  General: 'Versatile layout suitable for cross-industry proposals.',
}

function parseTemplates(raw: BackendTemplateEntry[]): CampaignTemplate[] {
  return raw.map(entry => ({
    id: `tmpl_${entry.product.toLowerCase()}`,
    name: `${entry.product} Template`,
    description: TEMPLATE_DESCRIPTIONS[entry.product] || 'Custom template for outreach.',
    layout: LAYOUT_MAP[entry.product] || 'editorial',
    target_categories: [entry.product],
    historical_effectiveness: entry.exists ? 0.82 : 0.5,
  }))
}

function parseCampaignStats(raw: BackendCampaignStats): Campaign[] {
  const campaigns: Campaign[] = []

  if (raw.by_product && Object.keys(raw.by_product).length > 0) {
    for (const [product, count] of Object.entries(raw.by_product)) {
      campaigns.push({
        id: `camp_${product.toLowerCase()}`,
        name: `${product} Campaign`,
        status: 'New',
        leads_count: count,
        opened_count: 0,
        replied_count: 0,
        meetings_booked: 0,
        created_at: new Date().toISOString(),
      })
    }
  }

  if (raw.by_status && Object.keys(raw.by_status).length > 0) {
    for (const [status, count] of Object.entries(raw.by_status)) {
      const validStatus = status as Campaign['status']
      const existing = campaigns.find(c => c.status === validStatus)
      if (existing) {
        existing.leads_count = count
      } else {
        campaigns.push({
          id: `status_${status.toLowerCase()}`,
          name: `${status} Leads`,
          status: validStatus,
          leads_count: count,
          opened_count: status === 'Opened' || status === 'Replied' || status === 'Meeting Booked' ? count : 0,
          replied_count: status === 'Replied' || status === 'Meeting Booked' ? count : 0,
          meetings_booked: status === 'Meeting Booked' ? count : 0,
          created_at: new Date().toISOString(),
        })
      }
    }
  }

  return campaigns.length > 0
    ? campaigns
    : [{ id: 'camp_default', name: 'All Campaigns', status: 'New', leads_count: raw.total, opened_count: 0, replied_count: 0, meetings_booked: 0, created_at: new Date().toISOString() }]
}

function parseFollowUpRule(raw: BackendFollowUpConfig): FollowUpRule {
  return {
    initial_delay_days: raw.initial_delay_days,
    loop_cycle_days: raw.cadence_days,
    max_follow_ups: raw.max_follow_ups,
    excluded_leads: [],
  }
}

function parseAnalytics(raw: BackendAnalyticsSummary): AnalyticsMetric[] {
  return [
    { label: 'Total Leads', value: raw.total_leads, unit: '', trend: 'stable', change: 0 },
    { label: 'Emails Sent', value: raw.emails_sent, unit: '', trend: 'up', change: 0 },
    { label: 'Open Rate', value: raw.open_rate, unit: '%', trend: 'up', change: 0 },
    { label: 'Reply Rate', value: raw.reply_rate, unit: '%', trend: 'up', change: 0 },
    { label: 'Conversion Rate', value: raw.conversion_rate, unit: '%', trend: 'up', change: 0 },
  ]
}

export async function getTemplates(): Promise<CampaignTemplate[]> {
  const { data } = await api.get<{ templates: BackendTemplateEntry[] }>('/marketing/templates')
  return parseTemplates(data.templates || [])
}

export async function getCampaignStats(): Promise<Campaign[]> {
  const { data } = await api.get<BackendCampaignStats>('/marketing/campaign/stats')
  return parseCampaignStats(data)
}

export async function getFollowUpConfig(): Promise<FollowUpRule> {
  const { data } = await api.get<BackendFollowUpConfig>('/marketing/follow-up/config')
  return parseFollowUpRule(data)
}

export async function getAnalytics(): Promise<AnalyticsMetric[]> {
  const { data } = await api.get<BackendAnalyticsSummary>('/marketing/analytics/summary')
  return parseAnalytics(data)
}
