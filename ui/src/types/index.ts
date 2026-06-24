export interface Lead {
  id: string
  company_name: string
  sector: string
  location: string
  contact: string
  description: string
  source: string
  qualification_score: number
}

export interface Tender {
  id: string
  title: string
  description: string
  deadline: string
  url: string
  category: string
  source: string
  relevance_score: number
  days_remaining: number
  urgency: 'red' | 'amber' | 'green'
}

export interface SalesIntel {
  summary: string
  insights: string[]
  total_leads: number
  total_tenders: number
  cross_referenced_sources: SourceRecord[]
}

export interface SourceRecord {
  id: string
  title: string
  source: string
  snippet: string
  url: string
}

export interface EmailDraft {
  lead_name: string
  validated_email: string
  tender_requirements: string
  email_body: string
  subject: string
  personalization_score: number
}

export interface PipelineStepStatus {
  status: 'pending' | 'active' | 'completed' | 'rejected'
  data: unknown
  explanation: string
}

export interface CopilotSession {
  session_id: string
  query: string
  status: string
  steps: Record<string, PipelineStepStatus>
  created_at: string
  sent_at?: string
}

export interface ActivityEntry {
  id: string
  timestamp: string
  type: 'ai_suggestion' | 'human_approval' | 'human_edit' | 'human_rejection' | 'system'
  step: string
  message: string
}

export interface CampaignTemplate {
  id: string
  name: string
  description: string
  layout: string
  target_categories: string[]
  historical_effectiveness: number
}

export interface Campaign {
  id: string
  name: string
  status: 'New' | 'Sent' | 'Opened' | 'Replied' | 'Meeting Booked'
  leads_count: number
  opened_count: number
  replied_count: number
  meetings_booked: number
  created_at: string
}

export interface FollowUpRule {
  initial_delay_days: number
  loop_cycle_days: number
  max_follow_ups: number
  excluded_leads: string[]
}

export interface SearchResult {
  id: string
  name: string
  sector: string
  location: string
  description: string
  contact: string
  link: string
}

export interface AnalyticsMetric {
  label: string
  value: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  change: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: Array<{ title: string; snippet: string; url?: string }>
}

export interface EndpointInfo {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  path: string
  description: string
  section: string
  access: 'page' | 'command' | 'both'
  command?: string
}

export interface DemoState {
  mode: 'sales' | 'marketing' | 'ai'
  salesState: number
  marketingState: number
  query: string
  loading: boolean
  routingStatus: string
  sessionId: string
  error: string
  leads: Lead[]
  tenders: Tender[]
  intel: SalesIntel | null
  emailDraft: EmailDraft | null
  templates: CampaignTemplate[]
  campaigns: Campaign[]
  followUpRule: FollowUpRule
  analytics: AnalyticsMetric[]
  activities: ActivityEntry[]
  searchResults: SearchResult[]
  searchQuery: string
  searchLoading: boolean
}
