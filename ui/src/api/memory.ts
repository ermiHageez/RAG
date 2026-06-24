import axios from 'axios'

const api = axios.create({ baseURL: '/', timeout: 30000 })

export async function getMemory(memoryType: string) {
  const { data } = await api.get(`/memory/${memoryType}`)
  return data
}

export async function saveMemory(memoryType: string, payload: { role: string; content: string }) {
  const { data } = await api.post(`/memory/${memoryType}`, payload)
  return data
}
