import axios from 'axios'
import type { Lead, Tender, SalesIntel, EmailDraft } from '../types'

const api = axios.create({
  baseURL: '/',
  timeout: 120000,
})

interface CopilotStep {
  status: string
  data: unknown
  explanation: string
}

interface CopilotRunResponse {
  session_id: string
  query: string
  steps: Record<string, CopilotStep>
}

interface ParsedCopilotData {
  sessionId: string
  leads: Lead[]
  tenders: Tender[]
  intel: SalesIntel | null
  emailDraft: EmailDraft | null
  route: string[]
}

function parseLead(data: Record<string, unknown>): Lead {
  return {
    id: data.id as string || `lead_${Math.random().toString(36).slice(2, 8)}`,
    company_name: (data.company_name || data.name || 'Unknown') as string,
    sector: (data.sector || 'General') as string,
    location: (data.location || 'Unknown') as string,
    contact: (data.contact || '') as string,
    description: (data.description || '') as string,
    source: (data.source || 'AI Discovery') as string,
    qualification_score: typeof data.qualification_score === 'number' ? data.qualification_score : 0.5,
  }
}

function parseTender(data: Record<string, unknown>): Tender {
  return {
    id: data.id as string || `tender_${Math.random().toString(36).slice(2, 8)}`,
    title: (data.title || 'Unknown Tender') as string,
    description: (data.description || '') as string,
    deadline: (data.deadline || '') as string,
    url: (data.url || '') as string,
    category: (data.category || 'General') as string,
    source: (data.source || 'AI Discovery') as string,
    relevance_score: typeof data.relevance_score === 'number' ? data.relevance_score : 0.5,
    days_remaining: typeof data.days_remaining === 'number' ? data.days_remaining : 30,
    urgency: (data.urgency || 'amber') as Tender['urgency'],
  }
}

function parseEmailDraft(data: Record<string, unknown> | null): EmailDraft | null {
  if (!data || !data.email_body) return null
  return {
    lead_name: (data.lead_name || 'Unknown') as string,
    validated_email: (data.validated_email || '') as string,
    tender_requirements: (data.tender_requirements || '') as string,
    email_body: (data.email_body || '') as string,
    subject: (data.subject || 'No Subject') as string,
    personalization_score: typeof data.personalization_score === 'number' ? data.personalization_score : 0.5,
  }
}

function parseIntel(data: Record<string, unknown> | null): SalesIntel | null {
  if (!data) return null
  return {
    summary: (data.summary || 'Analysis complete.') as string,
    insights: (data.insights || []) as string[],
    total_leads: typeof data.total_leads === 'number' ? data.total_leads : 0,
    total_tenders: typeof data.total_tenders === 'number' ? data.total_tenders : 0,
    cross_referenced_sources: (data.cross_referenced_sources || []) as SalesIntel['cross_referenced_sources'],
  }
}

export async function runCopilot(query: string): Promise<ParsedCopilotData> {
  const { data } = await api.post<CopilotRunResponse>('/copilot/run', { query })
  const steps = data.steps

  const rawLeads = (steps.leads?.data || []) as Record<string, unknown>[]
  const rawTenders = (steps.tenders?.data || []) as Record<string, unknown>[]
  const rawIntel = steps.intel?.data as Record<string, unknown> | null
  const rawEmail = steps.email?.data as Record<string, unknown> | null
  const sup = steps.supervisor as unknown as Record<string, unknown>
  const route = (sup?.route as string[]) || []

  return {
    sessionId: data.session_id,
    leads: Array.isArray(rawLeads) ? rawLeads.map(parseLead) : [],
    tenders: Array.isArray(rawTenders) ? rawTenders.map(parseTender) : [],
    intel: parseIntel(rawIntel),
    emailDraft: parseEmailDraft(rawEmail),
    route,
  }
}
