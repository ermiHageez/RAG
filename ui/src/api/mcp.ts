import axios from 'axios'
import type { SearchResult } from '../types'

const api = axios.create({
  baseURL: '/',
  timeout: 30000,
})

interface McpSearchResponse {
  success: boolean
  results: Array<{
    name: string
    sector: string
    location: string
    description: string
    contact: string
    link: string
  }>
  total: number
}

export async function searchMcp(query: string): Promise<SearchResult[]> {
  const { data } = await api.post<McpSearchResponse>('/mcp/search', { query })
  if (!data.success) throw new Error('MCP search failed')
  return data.results.map((r, i) => ({
    id: `search_${i}`,
    name: r.name,
    sector: r.sector,
    location: r.location,
    description: r.description,
    contact: r.contact,
    link: r.link,
  }))
}
