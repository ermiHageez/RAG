import axios from 'axios'

const api = axios.create({
  baseURL: '/',
  timeout: 30000,
})

export interface ApproveSendRequest {
  session_id: string
  email_subject: string
  email_body: string
}

export interface ApproveSendResponse {
  session_id: string
  status: string
  message: string
  n8n_response?: Record<string, unknown>
}

export async function approveSend(req: ApproveSendRequest): Promise<ApproveSendResponse> {
  const { data } = await api.post<ApproveSendResponse>('/copilot/approve-send', req)
  return data
}
