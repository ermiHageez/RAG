import axios from 'axios'
import type { ChatMessage } from '../types'

const api = axios.create({
  baseURL: '/',
  timeout: 60000,
})

interface RagChatResponse {
  session_id: string
  response: string
  sources: Array<{ title: string; snippet: string; url?: string }>
}

export async function ragChat(
  sessionId: string,
  message: string,
  history: ChatMessage[],
): Promise<RagChatResponse> {
  const historyPayload = history.map(m => ({
    role: m.role,
    content: m.content,
  }))

  try {
    const { data } = await api.post<RagChatResponse>('/rag/chat', {
      session_id: sessionId,
      message,
      history: historyPayload,
    })
    return data
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      throw new Error(error.response.data.detail)
    }
    throw error
  }
}
