import axios from 'axios'

const api = axios.create({ baseURL: '/', timeout: 60000 })

export async function uploadRagFile(file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/rag/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function getRagStatus() {
  const { data } = await api.get('/rag/status')
  return data
}

export async function rebuildRag() {
  const { data } = await api.post('/rag/rebuild')
  return data
}

export async function queryRag(query: string, top_k = 5) {
  const { data } = await api.post('/rag/query', { query, top_k })
  return data
}
