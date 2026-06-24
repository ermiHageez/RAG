import axios from 'axios'

const api = axios.create({ baseURL: '/', timeout: 60000 })

export interface McpTool {
  name: string
  description: string
}

export async function listMcpTools() {
  const { data } = await api.get<{ tools: McpTool[] }>('/mcp/tools')
  return data
}

export async function mcpTenders(query: string) {
  const { data } = await api.post<{ tenders: unknown[] }>('/mcp/tenders', { query })
  return data
}

export async function mcpDirectory(sector: string) {
  const { data } = await api.post<{ companies: unknown[] }>('/mcp/directory', { sector })
  return data
}
