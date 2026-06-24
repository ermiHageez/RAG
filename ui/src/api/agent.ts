import axios from 'axios'

const api = axios.create({ baseURL: '/', timeout: 60000 })

export interface AgentRunResponse {
  session_id: string
  status: string
  result: Record<string, unknown>
  steps: Record<string, { status: string; explanation: string }>
}

export async function runAgent(query: string) {
  const { data } = await api.post<AgentRunResponse>('/agent/run', { query })
  return data
}

export async function runSupervisor(query: string) {
  const { data } = await api.post<{ route: string; confidence: number; explanation: string }>('/agent/supervisor', { query })
  return data
}

export async function searchLeads(query: string) {
  const { data } = await api.post<{ leads: unknown[] }>('/agent/leads', { query })
  return data
}

export async function searchTenders(query: string) {
  const { data } = await api.post<{ tenders: unknown[] }>('/agent/tenders', { query })
  return data
}

export async function knowledgeSearch(query: string) {
  const { data } = await api.post<{ results: unknown[] }>('/agent/knowledge', { query })
  return data
}

export async function salesIntelligence(query: string) {
  const { data } = await api.post<{ intel: unknown }>('/agent/sales-intel', { query })
  return data
}

export async function draftContent(query: string) {
  const { data } = await api.post<{ draft: unknown }>('/agent/content', { query })
  return data
}

export async function runApproval(id: string) {
  const { data } = await api.post<{ approved: boolean; message: string }>('/agent/approval', { id })
  return data
}
