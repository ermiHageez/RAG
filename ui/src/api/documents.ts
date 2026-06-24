import axios from 'axios'

const api = axios.create({ baseURL: '/', timeout: 30000 })

export async function downloadDocument(sessionId: string) {
  const { data } = await api.get(`/doc-gen/download/${sessionId}`, { responseType: 'blob' })
  return data
}
