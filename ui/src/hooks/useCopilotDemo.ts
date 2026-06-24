import { useState, useCallback, useRef } from 'react'
import type {
  DemoState, Lead, Tender, SalesIntel, EmailDraft,
  CampaignTemplate, FollowUpRule, AnalyticsMetric, ActivityEntry, SearchResult,
} from '../types'
import { searchMcp } from '../api/mcp'
import { runCopilot } from '../api/copilot'
import { approveSend } from '../api/copilotApprove'
import { getTemplates, getCampaignStats, getFollowUpConfig, getAnalytics } from '../api/marketing'

const emptyState: DemoState = {
  mode: 'sales',
  salesState: 0,
  marketingState: 0,
  query: '',
  loading: false,
  routingStatus: '',
  sessionId: '',
  error: '',
  leads: [],
  tenders: [],
  intel: null,
  emailDraft: null,
  templates: [],
  campaigns: [],
  followUpRule: { initial_delay_days: 3, loop_cycle_days: 7, max_follow_ups: 3, excluded_leads: [] },
  analytics: [],
  activities: [],
  searchResults: [],
  searchQuery: '',
  searchLoading: false,
}

export function useCopilotDemo() {
  const [state, setState] = useState<DemoState>(emptyState)
  const activityId = useRef(0)

  const addActivity = useCallback((entry: Omit<ActivityEntry, 'id' | 'timestamp'>) => {
    activityId.current += 1
    setState(prev => ({
      ...prev,
      activities: [{
        ...entry,
        id: `act_${activityId.current}`,
        timestamp: new Date().toISOString(),
      }, ...prev.activities.slice(0, 49)],
    }))
  }, [])

  const setMode = useCallback((mode: 'sales' | 'marketing' | 'ai') => {
    setState({ ...emptyState, mode })
    activityId.current = 0
  }, [])

  const run = useCallback(async (query: string) => {
    const isSales = state.mode === 'sales'

    setState(prev => ({
      ...prev,
      query,
      loading: true,
      error: '',
      routingStatus: isSales ? 'Classified as: lead + tender' : 'Classified as: marketing template generation',
      salesState: isSales ? 1 : 0,
      marketingState: isSales ? 0 : 1,
    }))
    addActivity({ type: 'ai_suggestion', step: 'supervisor', message: `AI classified query → route: ${isSales ? 'lead + tender' : 'marketing template generation'}` })

    try {
      if (isSales) {
        const result = await runCopilot(query)
        setState(prev => ({
          ...prev,
          loading: false,
          salesState: 2,
          sessionId: result.sessionId,
          leads: result.leads,
          tenders: result.tenders,
          intel: result.intel,
          emailDraft: result.emailDraft,
        }))
        addActivity({ type: 'ai_suggestion', step: 'leads', message: `AI completed lead discovery — ${result.leads.length} leads found` })
        if (result.tenders.length > 0) {
          addActivity({ type: 'ai_suggestion', step: 'tenders', message: `AI completed tender assessment — ${result.tenders.length} tenders matched` })
        }
        if (result.emailDraft) {
          addActivity({ type: 'ai_suggestion', step: 'email', message: `AI generated personalized outreach email — score: ${(result.emailDraft.personalization_score * 100).toFixed(0)}%` })
        }
      } else {
        const [templates, campaigns, followUpRule] = await Promise.all([
          getTemplates(),
          getCampaignStats(),
          getFollowUpConfig(),
        ])
        setState(prev => ({
          ...prev,
          loading: false,
          marketingState: 2,
          templates,
          campaigns,
          followUpRule,
        }))
        addActivity({ type: 'ai_suggestion', step: 'templates', message: `AI retrieved ${templates.length} campaign templates for your review` })
      }
    } catch {
      setState(prev => ({
        ...prev,
        loading: false,
        salesState: 0,
        marketingState: 0,
        error: 'Backend API unavailable — please ensure the server is running',
      }))
      addActivity({ type: 'system', step: 'api', message: 'Backend API unavailable' })
    }
  }, [state.mode, addActivity])

  const advance = useCallback((step: string) => {
    const isSales = state.mode === 'sales'

    if (isSales) {
      switch (state.salesState) {
        case 2: {
          addActivity({ type: 'human_approval', step: 'approval', message: 'You approved the deal — proceeding to final gate' })
          setState(prev => ({ ...prev, salesState: 6 }))
          addActivity({ type: 'system', step: 'approval', message: 'Awaiting final approval to send' })
          break
        }
      }
    } else {
      switch (state.marketingState) {
        case 2: {
          addActivity({ type: 'human_approval', step: 'template', message: 'Template selected — opening campaign launchpad' })
          setState(prev => ({ ...prev, marketingState: 3 }))
          break
        }
        case 3: {
          addActivity({ type: 'human_approval', step: 'pipeline', message: 'Launchpad configured — generating email preview' })
          setState(prev => {
            const campaignName = prev.campaigns[0]?.name || 'Campaign'
            return {
              ...prev,
              marketingState: 5,
              emailDraft: {
                lead_name: campaignName,
                validated_email: 'campaigns@etech.com',
                tender_requirements: 'Campaign deployment',
                email_body: `Campaign: ${campaignName} - Follow-up sequence configured with ${prev.followUpRule.max_follow_ups} touches every ${prev.followUpRule.loop_cycle_days} days.`,
                subject: `${campaignName} Outreach`,
                personalization_score: 0.5,
              },
            }
          })
          addActivity({ type: 'ai_suggestion', step: 'email', message: 'Email preview generated with campaign content' })
          break
        }
        case 5: {
          addActivity({ type: 'human_approval', step: 'email', message: 'Preview approved — proceeding to deployment gate' })
          setState(prev => ({ ...prev, marketingState: 6 }))
          addActivity({ type: 'system', step: 'approval', message: 'Campaign ready for final deployment approval' })
          break
        }
      }
    }
  }, [state, addActivity])

  const sendingRef = useRef(false)

  const handleApproveSend = useCallback(async () => {
    const isSales = state.mode === 'sales'
    const currentState = isSales ? state.salesState : state.marketingState
    if (currentState !== 6) return
    if (sendingRef.current) return
    sendingRef.current = true

    try {
      if (state.sessionId && state.emailDraft) {
        await approveSend({
          session_id: state.sessionId,
          email_subject: state.emailDraft.subject,
          email_body: state.emailDraft.email_body,
        })
      }

      let analytics: AnalyticsMetric[] = []
      try {
        analytics = await getAnalytics()
      } catch {}

      if (isSales) {
        addActivity({ type: 'human_approval', step: 'approval', message: 'You approved and sent — campaign deployed' })
        setState(prev => ({ ...prev, salesState: 7, analytics }))
        addActivity({ type: 'system', step: 'complete', message: 'Co-Pilot completed — time saved and metrics tracked' })
      } else {
        addActivity({ type: 'human_approval', step: 'approval', message: 'You approved and dispatched campaign — monitoring telemetry' })
        setState(prev => ({ ...prev, marketingState: 7, analytics }))
        addActivity({ type: 'system', step: 'complete', message: 'Campaign deployed — tracking open rates and engagement' })
      }
    } catch {
      setState(prev => ({ ...prev, error: 'Send failed — backend unreachable' }))
    } finally {
      sendingRef.current = false
    }
  }, [state, addActivity])

  const search = useCallback(async (query: string) => {
    setState(prev => ({ ...prev, searchQuery: query, searchLoading: true, searchResults: [] }))
    try {
      const results = await searchMcp(query)
      setState(prev => ({ ...prev, searchResults: results, searchLoading: false }))
      addActivity({ type: 'ai_suggestion', step: 'search', message: `MCP search returned ${results.length} results for "${query}"` })
    } catch {
      setState(prev => ({ ...prev, searchLoading: false }))
      addActivity({ type: 'system', step: 'search', message: `Search failed for "${query}"` })
    }
  }, [addActivity])

  const addSearchResultToPipeline = useCallback((result: SearchResult) => {
    const newLead: Lead = {
      id: `lead_search_${Date.now()}`,
      company_name: result.name,
      sector: result.sector,
      location: result.location,
      contact: result.contact,
      description: result.description.slice(0, 200),
      source: `MCP Search: ${result.link}`,
      qualification_score: 0.5,
    }
    setState(prev => ({
      ...prev,
      leads: [...prev.leads, newLead],
      salesState: prev.salesState < 2 ? 2 : prev.salesState,
      query: prev.query || `Search: ${result.name}`,
    }))
    addActivity({ type: 'human_approval', step: 'leads', message: `You added "${result.name}" to pipeline from search results` })
  }, [addActivity])

  const handleEmailEdit = useCallback((subject: string, body: string) => {
    addActivity({ type: 'human_edit', step: 'email', message: 'You edited the email draft' })
    setState(prev => ({
      ...prev,
      emailDraft: prev.emailDraft ? { ...prev.emailDraft, subject, email_body: body } : prev.emailDraft,
    }))
  }, [addActivity])

  const handleTestSend = useCallback(async () => {
    addActivity({ type: 'system', step: 'email', message: 'Test email requested — sending preview' })
    try {
      if (state.sessionId && state.emailDraft) {
        await approveSend({
          session_id: state.sessionId,
          email_subject: `[TEST] ${state.emailDraft.subject}`,
          email_body: state.emailDraft.email_body,
        })
      }
      addActivity({ type: 'system', step: 'email', message: 'Test email sent successfully' })
    } catch {
      addActivity({ type: 'system', step: 'email', message: 'Test email failed — backend unreachable' })
    }
  }, [state, addActivity])

  const dismissError = useCallback(() => {
    setState(prev => ({ ...prev, error: '' }))
  }, [])

  const reset = useCallback(() => {
    setState(emptyState)
    activityId.current = 0
  }, [])

  return {
    state, setMode, run, advance, handleApproveSend, handleTestSend,
    search, addSearchResultToPipeline, handleEmailEdit, dismissError, reset,
  }
}
