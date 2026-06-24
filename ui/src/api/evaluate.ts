import axios from 'axios'

const api = axios.create({ baseURL: '/', timeout: 120000 })

export interface EvalResponse {
  status: string
  results: Record<string, unknown>
}

export async function evaluateRag() {
  const { data } = await api.post<EvalResponse>('/evaluate/rag')
  return data
}

export async function evaluateRouting() {
  const { data } = await api.post<EvalResponse>('/evaluate/routing')
  return data
}

export async function evaluateContent() {
  const { data } = await api.post<EvalResponse>('/evaluate/content')
  return data
}
