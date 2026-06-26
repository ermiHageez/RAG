import { useState, useCallback, useRef } from 'react'
import { Box, Typography, Button, Chip, Dialog } from '@mui/material'
import RestartAltIcon from '@mui/icons-material/RestartAlt'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import SearchIcon from '@mui/icons-material/Search'
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder'
import SmartToyIcon from '@mui/icons-material/SmartToy'

import CopilotLayout from './components/CopilotLayout'
import QueryInput from './components/QueryInput'
import LeadReview from './components/LeadReview'
import TenderReview from './components/TenderReview'
import IntelReview from './components/IntelReview'
import EmailEditor from './components/EmailEditor'
import ApprovalGate from './components/ApprovalGate'
import ActivityFeed from './components/ActivityFeed'
import CampaignTemplateEngine from './components/CampaignTemplateEngine'
import CampaignTracker from './components/CampaignTracker'
import FollowUpScheduler from './components/FollowUpScheduler'
import AnalyticsDashboard from './components/AnalyticsDashboard'
import SearchResults from './components/SearchResults'
import DealWorkspace from './components/DealWorkspace'
import CampaignLaunchpad from './components/CampaignLaunchpad'
import ChatInterface from './components/ChatInterface'
import ApiExplorer from './components/ApiExplorer'
import AiHub from './components/AiHub'
import RagConsole from './components/RagConsole'
import MemoryVault from './components/MemoryVault'
import EvaluationLab from './components/EvaluationLab'
import DocumentManager from './components/DocumentManager'
import { useCopilotDemo } from './hooks/useCopilotDemo'
import { ragChat } from './api/chat'
import { runAgent, runSupervisor, searchLeads, searchTenders, knowledgeSearch, salesIntelligence, draftContent, runApproval } from './api/agent'
import { getRagStatus, queryRag, rebuildRag } from './api/rag'
import { listMcpTools, mcpTenders, mcpDirectory } from './api/tools'
import { searchMcp } from './api/mcp'
import { getMemory, saveMemory } from './api/memory'
import { evaluateRag, evaluateRouting, evaluateContent } from './api/evaluate'
import { downloadDocument } from './api/documents'
import { approveSend } from './api/copilotApprove'
import type { CampaignTemplate, Campaign, SearchResult, FollowUpRule, ChatMessage } from './types'

export default function App() {
  const {
    state, setMode, run, advance, handleApproveSend, handleTestSend,
    search, addSearchResultToPipeline, handleEmailEdit, dismissError, reset,
  } = useCopilotDemo()

  const [activeNav, setActiveNav] = useState('home')
  const [pipelineAddedIds, setPipelineAddedIds] = useState<Set<string>>(new Set())
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatLoading, setChatLoading] = useState(false)
  const [loadingLabel, setLoadingLabel] = useState('')
  const chatSessionRef = useRef({ sales: '', marketing: '', ai: '' })

  const isSales = state.mode === 'sales'
  const isAi = state.mode === 'ai'
  const flowState = isSales ? state.salesState : state.marketingState
  const isComplete = flowState === 7
  const isIdle = flowState === 0
  const showApprovalOverlay = flowState === 6

  const handleNavChange = useCallback((key: string) => {
    setActiveNav(key)
  }, [])

  const handleModeChange = useCallback((mode: 'sales' | 'marketing' | 'ai') => {
    setMode(mode)
    setChatMessages([])
    if (mode === 'sales') setActiveNav('home')
    else if (mode === 'marketing') setActiveNav('campaign-control')
    else setActiveNav('ai-home')
  }, [setMode])

  const handleRun = useCallback((query: string) => {
    run(query)
    setActiveNav(isSales ? 'deal-board' : 'content-library')
  }, [run, isSales])

  const handleTemplateSelect = useCallback(() => {
    advance('template')
    setActiveNav('live-pipelines')
  }, [advance])

  const handleLaunchpadPreview = useCallback(() => {
    advance('preview')
    setActiveNav('campaign-control')
  }, [advance])

  const handleDownload = useCallback(() => {
    alert('Simulating download of print-ready HTML proposal document from /doc-gen/download/{id}')
  }, [])

  const handleStatusOverride = useCallback((_campaignId: string, _newStatus: CampaignTemplate['target_categories'][0]) => {
    advance('pipeline')
  }, [advance])

const handleFollowUpUpdate = useCallback((_rule: FollowUpRule) => {
    advance('automation')
}, [advance])

  const handleFinalReject = useCallback(() => {
    reset()
    setActiveNav('home')
  }, [reset])

  const handleSave = useCallback(() => {
    reset()
    setActiveNav('home')
  }, [reset])

  const handleNotesChange = useCallback((_notes: string) => {
  }, [])

  const handleAddToPipeline = useCallback((result: SearchResult) => {
    addSearchResultToPipeline(result)
    setPipelineAddedIds(prev => new Set(prev).add(result.name + result.link))
    setActiveNav('deal-board')
  }, [addSearchResultToPipeline])

  const handleDeployDeal = useCallback(() => {
    advance('deploy')
  }, [advance])

  const handleCommand = useCallback(async (cmd: string, args: string, userMsg: ChatMessage) => {
    let result: string
    try {
      switch (cmd) {
        case 'run-agent': { const r = await runAgent(args); result = JSON.stringify(r, null, 2); break }
        case 'supervisor': { const r = await runSupervisor(args); result = JSON.stringify(r, null, 2); break }
        case 'search-leads': { const r = await searchLeads(args); result = JSON.stringify(r, null, 2); break }
        case 'search-tenders': { const r = await searchTenders(args); result = JSON.stringify(r, null, 2); break }
        case 'knowledge': { const r = await knowledgeSearch(args); result = JSON.stringify(r, null, 2); break }
        case 'sales-intel': { const r = await salesIntelligence(args); result = JSON.stringify(r, null, 2); break }
        case 'draft-content': { const r = await draftContent(args); result = JSON.stringify(r, null, 2); break }
        case 'approve': { const r = await runApproval(args); result = JSON.stringify(r, null, 2); break }
        case 'rag-status': { const r = await getRagStatus(); result = JSON.stringify(r, null, 2); break }
        case 'rag-query': { const r = await queryRag(args); result = JSON.stringify(r, null, 2); break }
        case 'rag-rebuild': { const r = await rebuildRag(); result = JSON.stringify(r, null, 2); break }
        case 'mcp-tools': { const r = await listMcpTools(); result = JSON.stringify(r, null, 2); break }
        case 'tenders': { const r = await mcpTenders(args); result = JSON.stringify(r, null, 2); break }
        case 'directory': { const r = await mcpDirectory(args); result = JSON.stringify(r, null, 2); break }
        case 'make-search': {
          const q = args.trim()
          if (!q) { result = 'Usage: /make-search <company name or keyword>'; break }
          const r = await searchMcp(q)
          result = r.length === 0
            ? `No results found for "${q}". Try different keywords.`
            : `**Search results for "${q}"**\n\n` + r.map((item, i) =>
                `**${i+1}. ${item.name}**\n` +
                `- Sector: ${item.sector}\n` +
                `- Location: ${item.location}\n` +
                `- Contact: ${item.contact}\n` +
                `- ${item.description}` + (item.link ? `\n- Link: ${item.link}` : '')
              ).join('\n\n') + `\n\n_Total: ${r.length} results_`
          break
        }
        case 'memory': { const r = await getMemory(args || 'conversation'); result = JSON.stringify(r, null, 2); break }
        case 'remember': { const idx = args.indexOf(':'); if (idx === -1) { result = 'Usage: /remember <role>: <content>'; break }; const r = await saveMemory('custom', { role: args.slice(0, idx).trim(), content: args.slice(idx + 1).trim() }); result = JSON.stringify(r, null, 2); break }
        case 'eval-rag': { const r = await evaluateRag(); result = JSON.stringify(r, null, 2); break }
        case 'eval-routing': { const r = await evaluateRouting(); result = JSON.stringify(r, null, 2); break }
        case 'eval-content': { const r = await evaluateContent(); result = JSON.stringify(r, null, 2); break }
        case 'new-deal': { const r = await runAgent('new deal'); result = JSON.stringify(r, null, 2); break }
        case 'generate-proposal': { const r = await downloadDocument('latest'); result = 'Proposal generated (check Document Manager)'; break }
        case 'approve-send': { const r = await approveSend({ session_id: args, email_subject: '', email_body: '' }); result = JSON.stringify(r, null, 2); break }
        case 'reset-session': { const r = await runAgent('reset'); result = JSON.stringify(r, null, 2); break }
        case 'get-template': { result = `Use Marketing > Content Library to view template: ${args}`; break }
        case 'update-template': { result = `Use Marketing > Content Library to update template: ${args}`; break }
        case 'campaign-leads': { result = 'Use Marketing > Live Pipelines to view campaign leads'; break }
        case 'update-lead-status': { result = `Update lead status via Marketing > Live Pipelines: ${args}`; break }
        case 'check-followups': { result = 'Follow-up check triggered (via Marketing > Automation Rules)'; break }
        case 'followup-schedule': { result = `View schedule in Marketing > Automation Rules for: ${args}`; break }
        case 'update-followup-config': { result = 'Update config in Marketing > Automation Rules'; break }
        case 'analytics-products': { result = 'View in Marketing > Analytics'; break }
        case 'analytics-timeline': { result = 'View timeline in Marketing > Analytics'; break }
        case 'export-analytics': { result = 'Export from Marketing > Analytics'; break }
        case 'download-proposal': { const blob = await downloadDocument(args); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `proposal-${args}.pdf`; a.click(); URL.revokeObjectURL(url); result = `Downloading proposal ${args}...`; break }
        case 'help': result = 'Available commands:\n' + Object.keys(commandMap).join(', '); break
        default: result = `Unknown command: /${cmd}. Type /help for available commands.`; break
      }
    } catch (err) {
      result = `Error: ${err instanceof Error ? err.message : 'Command failed'}`
    }
    return {
      id: `chat_cmd_${Date.now()}`,
      role: 'assistant' as const,
      content: result,
      timestamp: new Date().toISOString(),
    }
  }, [])

  const commandMap: Record<string, boolean> = {
    'run-agent': true, 'supervisor': true, 'search-leads': true, 'search-tenders': true,
    'knowledge': true, 'sales-intel': true, 'draft-content': true, 'approve': true,
    'rag-status': true, 'rag-query': true, 'rag-rebuild': true, 'mcp-tools': true,
    'tenders': true, 'directory': true, 'make-search': true, 'memory': true, 'remember': true,
    'eval-rag': true, 'eval-routing': true, 'eval-content': true, 'new-deal': true,
    'generate-proposal': true, 'approve-send': true, 'reset-session': true,
    'get-template': true, 'update-template': true, 'campaign-leads': true,
    'update-lead-status': true, 'check-followups': true, 'followup-schedule': true,
    'update-followup-config': true, 'analytics-products': true, 'analytics-timeline': true,
    'export-analytics': true, 'download-proposal': true, 'help': true,
  }

  const handleChatSend = useCallback(async (message: string) => {
    const userMsg: ChatMessage = {
      id: `chat_user_${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    }
    setChatMessages(prev => [...prev, userMsg])
    setChatLoading(true)

    let isSearchCmd = false
    if (message.startsWith('/')) {
      const spaceIdx = message.indexOf(' ')
      const cmd = spaceIdx === -1 ? message.slice(1).toLowerCase() : message.slice(1, spaceIdx).toLowerCase()
      if (cmd === 'make-search') isSearchCmd = true
    }
    setLoadingLabel(isSearchCmd ? 'AI is searching Ethiopian enterprises...' : 'Thinking...')

    try {
      let assistantMsg: ChatMessage

      if (message.startsWith('/')) {
        const spaceIdx = message.indexOf(' ')
        const cmd = spaceIdx === -1 ? message.slice(1).toLowerCase() : message.slice(1, spaceIdx).toLowerCase()
        const args = spaceIdx === -1 ? '' : message.slice(spaceIdx + 1)
        assistantMsg = await handleCommand(cmd, args, userMsg)
      } else {
        const mode = state.mode
        const ref = chatSessionRef.current
        if (!ref[mode]) {
          ref[mode] = `chat_${mode}_${Date.now()}`
        }
        const sessionId = ref[mode]
        const data = await ragChat(sessionId, message, chatMessages.concat(userMsg))
        assistantMsg = {
          id: `chat_ai_${Date.now()}`,
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString(),
          sources: data.sources.map(s => ({
            title: s.title,
            snippet: s.snippet,
            url: s.url || undefined,
          })),
        }
      }

      setChatMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      const detail = err instanceof Error ? err.message : ''
      const errorMsg: ChatMessage = {
        id: `chat_err_${Date.now()}`,
        role: 'assistant',
        content: detail || 'Error: Backend API unreachable. Please ensure the server is running.',
        timestamp: new Date().toISOString(),
      }
      setChatMessages(prev => [...prev, errorMsg])
    } finally {
      setChatLoading(false)
      setLoadingLabel('')
    }
  }, [state.mode, chatMessages, handleCommand])

  // ─── Loading Spinner ────────────────────────────────────────────────

  const renderLoading = () => (
    <Box sx={{ textAlign: 'center', py: 4 }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1.5 }}>
        <Box sx={{ width: 32, height: 32, border: '2px solid rgba(0,200,83,0.3)', borderTopColor: '#00c853', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
        <Typography variant="body2" color="#9aa0a6">Computing route...</Typography>
        <Chip label={state.routingStatus} size="small" sx={{ background: 'rgba(0,200,83,0.1)', color: '#00c853', border: '1px solid rgba(0,200,83,0.3)', fontSize: 11 }} />
      </Box>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </Box>
  )

  // ─── Home View ──────────────────────────────────────────────────────

  const renderHome = () => (
    <>
      {isIdle && !state.loading && (
        <>
          <QueryInput onsubmit={handleRun} disabled={false} querySubmitted="" mode={state.mode} />
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Typography variant="body2" color="#5f6368">
              {isSales
                ? 'Type a query above to start, or use Deep Account Search to find leads manually.'
                : 'Type a query above to start. The co-pilot will design campaign templates, organize pipelines, and schedule follow-ups.'}
            </Typography>
          </Box>
        </>
      )}

      {state.query && !isIdle && !state.loading && (
        <QueryInput onsubmit={handleRun} disabled querySubmitted={state.query} mode={state.mode} />
      )}

      {state.loading && renderLoading()}

      {!isIdle && !isComplete && !state.loading && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
          <Button
            variant="outlined"
            startIcon={<RestartAltIcon />}
            onClick={() => { reset(); setActiveNav('home') }}
            sx={{ color: '#9aa0a6', borderColor: 'rgba(255,255,255,0.12)' }}
          >
            Start New Session
          </Button>
        </Box>
      )}
    </>
  )

  // ─── Deal Workspace View (Sales States 2-6) ─────────────────────────

  const renderDealWorkspace = () => {
    if (flowState < 2 || isComplete) return null

    return (
      <DealWorkspace
        leads={state.leads}
        tenders={state.tenders}
        intel={state.intel}
        emailDraft={state.emailDraft}
        onApprove={handleDeployDeal}
        onEmailEdit={handleEmailEdit}
        onRegenerate={() => handleEmailEdit('', '')}
        onNotesChange={handleNotesChange}
      />
    )
  }

  // ─── Approval Overlay (State 6) ─────────────────────────────────────

  const renderApprovalOverlay = () => (
    <Dialog
      open={showApprovalOverlay}
      onClose={() => {}}
      PaperProps={{
        sx: {
          background: '#1a1a1e',
          border: '1px solid rgba(255,255,255,0.12)',
          borderRadius: '8px',
          maxWidth: 480,
          width: '100%',
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ color: '#e8eaed', fontWeight: 600, mb: 2, fontSize: 16 }}>
          Final Approval Summary
        </Typography>
        <ApprovalGate
          leadCount={state.leads.length}
          tenderCount={state.tenders.length}
          hasDraft={!!state.emailDraft}
          onApprove={handleApproveSend}
          onReject={handleFinalReject}
          onSave={handleSave}
        />
      </Box>
    </Dialog>
  )

  // ─── Completed View (State 7) ───────────────────────────────────────

  const renderCompleted = () => (
    <>
      <Box sx={{
        background: '#1a1a1e',
        border: '1px solid rgba(0,200,83,0.3)',
        borderRadius: '6px',
        p: 4,
        textAlign: 'center',
        mb: 3,
      }}>
        <CheckCircleOutlineIcon sx={{ fontSize: 48, color: '#00c853', mb: 1 }} />
        <Typography variant="h5" fontWeight={600} color="#e8eaed" sx={{ mb: 0.5 }}>
          {isSales ? 'Co-Pilot Complete!' : 'Campaign Dispatched!'}
        </Typography>
        <Typography variant="body2" color="#9aa0a6" sx={{ mb: 2 }}>
          {isSales
            ? 'The proposal has been reviewed and queued for delivery.'
            : 'The campaign has been deployed and telemetry is being tracked.'}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap', mb: 2 }}>
          {isSales ? (
            <>
              <Chip label={`${state.leads.length} leads reviewed`} sx={{ background: 'rgba(0,200,83,0.1)', color: '#00c853', border: '1px solid rgba(0,200,83,0.3)' }} />
              <Chip label={`${state.tenders.length} tenders reviewed`} sx={{ background: 'rgba(0,200,83,0.1)', color: '#00c853', border: '1px solid rgba(0,200,83,0.3)' }} />
              <Chip label="Email approved" sx={{ background: 'rgba(0,200,83,0.1)', color: '#00c853', border: '1px solid rgba(0,200,83,0.3)' }} />
            </>
          ) : (
            <>
              <Chip label={`${state.campaigns.length} campaigns active`} sx={{ background: 'rgba(0,200,83,0.1)', color: '#00c853', border: '1px solid rgba(0,200,83,0.3)' }} />
              <Chip label="Template selected" sx={{ background: 'rgba(0,200,83,0.1)', color: '#00c853', border: '1px solid rgba(0,200,83,0.3)' }} />
              <Chip label="Automation configured" sx={{ background: 'rgba(0,200,83,0.1)', color: '#00c853', border: '1px solid rgba(0,200,83,0.3)' }} />
            </>
          )}
        </Box>
        <Button
          variant="outlined"
          startIcon={<RestartAltIcon />}
          onClick={() => { reset(); setActiveNav('home') }}
          sx={{ color: '#9aa0a6', borderColor: 'rgba(255,255,255,0.12)' }}
        >
          Start New Session
        </Button>
      </Box>

      {state.analytics.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <AnalyticsDashboard metrics={state.analytics} mode={state.mode} />
        </Box>
      )}

      {state.activities.length > 0 && (
        <ActivityFeed activities={state.activities} />
      )}
    </>
  )

  // ─── Marketing: Content Library (State 2) ────────────────────────────

  const renderContentLibrary = () => {
    if (state.loading) return renderLoading()
    if (flowState >= 2) {
      return (
        <CampaignTemplateEngine templates={state.templates} onSelect={handleTemplateSelect} />
      )
    }
    return (
      <Box sx={{ textAlign: 'center', py: 6 }}>
        <Typography variant="body2" color="#5f6368">
          No campaign active. Go to Campaign Control to start.
        </Typography>
      </Box>
    )
  }

  // ─── Marketing: Live Pipelines (State 3-4) ──────────────────────────

  const renderLivePipelines = () => {
    if (flowState >= 3) {
      return (
        <CampaignLaunchpad
          campaigns={state.campaigns}
          followUpRule={state.followUpRule}
          onStatusOverride={handleStatusOverride}
          onUpdateRule={handleFollowUpUpdate}
          onPreview={handleLaunchpadPreview}
        />
      )
    }
    return (
      <Box sx={{ textAlign: 'center', py: 6 }}>
        <Typography variant="body2" color="#5f6368">
          No pipeline data yet. Select a template first in Content Library.
        </Typography>
      </Box>
    )
  }

  // ─── Marketing: Automation Rules (global config) ────────────────────

  const renderAutomationRules = () => (
    <FollowUpScheduler rule={state.followUpRule} onUpdateRule={handleFollowUpUpdate} />
  )

  // ─── Sales: Performance Metrics ─────────────────────────────────────

  const renderMetrics = () => {
    if (state.analytics.length > 0) {
      return <AnalyticsDashboard metrics={state.analytics} mode={state.mode} />
    }
    return (
      <Box sx={{ textAlign: 'center', py: 6 }}>
        <Typography variant="body2" color="#5f6368">
          Complete a pipeline run to see performance metrics here.
        </Typography>
      </Box>
    )
  }

  // ─── Sales: System Audit Log ────────────────────────────────────────

  const renderAuditLog = () => (
    state.activities.length > 0
      ? <ActivityFeed activities={state.activities} />
      : (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="body2" color="#5f6368">
            No activity logged yet.
          </Typography>
        </Box>
      )
  )

  // ─── Saved Accounts (placeholder) ───────────────────────────────────

  const renderSavedAccounts = () => (
    <Box sx={{ textAlign: 'center', py: 6 }}>
      <BookmarkBorderIcon sx={{ fontSize: 48, color: '#5f6368', mb: 2 }} />
      <Typography variant="body2" color="#5f6368">
        Saved accounts will appear here. Use Deep Account Search to discover and save leads.
      </Typography>
    </Box>
  )

  // ─── AI Chat ────────────────────────────────────────────────────────

  const renderChat = () => (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Typography variant="h6" sx={{ color: '#e8eaed', mb: 1, fontSize: 15, fontWeight: 600 }}>
        <SmartToyIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-top' }} />
        {isAi
          ? 'AI Chat — Type /help for available commands'
          : `AI Chat with RAG — ${state.mode === 'sales' ? 'Sales' : 'Marketing'} Intelligence`}
      </Typography>
      <ChatInterface
        messages={chatMessages}
        onSend={handleChatSend}
        loading={chatLoading}
        loadingLabel={loadingLabel}
        showCommandHint={isAi}
        commands={Object.keys(commandMap)}
      />
    </Box>
  )

  // ─── AI Hub ─────────────────────────────────────────────────────────

  const renderAiHome = () => (
    <AiHub onNavigate={handleNavChange} />
  )

  const renderRagConsole = () => (
    <RagConsole />
  )

  const renderMemoryVault = () => (
    <MemoryVault />
  )

  const renderEvaluationLab = () => (
    <EvaluationLab />
  )

  const renderDocumentManager = () => (
    <DocumentManager />
  )

  const renderApiExplorer = () => (
    <ApiExplorer />
  )

  // ─── Marketing Preview (State 5) ────────────────────────────────────

  const renderMarketingPreview = () => {
    if (flowState >= 5 && state.emailDraft) {
      return (
        <Box sx={{ maxWidth: 700, mx: 'auto' }}>
          <Typography variant="h6" sx={{ color: '#e8eaed', mb: 2, fontSize: 15, fontWeight: 600 }}>
            Email Preview
          </Typography>
          <EmailEditor
            draft={state.emailDraft}
            onEdit={handleEmailEdit}
            onRegenerate={() => handleEmailEdit('', '')}
            onTestSend={handleTestSend}
            mode="marketing"
          />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2, gap: 1 }}>
            <Button
              variant="contained"
              onClick={() => advance('preview')}
              sx={{ background: '#00c853', color: '#121214', fontWeight: 600, '&:hover': { background: '#00e676' } }}
            >
              Approve & Deploy
            </Button>
            <Button
              variant="outlined"
              onClick={() => { reset(); setActiveNav('campaign-control') }}
              sx={{ color: '#9aa0a6', borderColor: 'rgba(255,255,255,0.12)' }}
            >
              Cancel
            </Button>
          </Box>
        </Box>
      )
    }
    return (
      <Box sx={{ textAlign: 'center', py: 6 }}>
        <Typography variant="body2" color="#5f6368">
          No email preview available. Configure the launchpad first.
        </Typography>
      </Box>
    )
  }

  // ─── Main Content Router ────────────────────────────────────────────

  const renderMainContent = () => {
    // Sales views
    if (isSales) {
      switch (activeNav) {
        case 'home':
        case 'campaign-control':
          return isComplete ? renderCompleted() : renderHome()

        case 'deal-board':
          if (state.loading) return renderLoading()
          if (isComplete) return renderCompleted()
          if (flowState >= 2) return renderDealWorkspace()
          return renderHome()

        case 'search':
          return (
            <Box>
              <Typography variant="h6" sx={{ color: '#e8eaed', mb: 2, fontSize: 15, fontWeight: 600 }}>
                <SearchIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-top' }} />
                Deep Account Search
              </Typography>
              <SearchResults
                results={state.searchResults}
                loading={state.searchLoading}
                onSearch={search}
                onAddToPipeline={handleAddToPipeline}
                addedIds={pipelineAddedIds}
              />
            </Box>
          )

        case 'metrics':
          return renderMetrics()

        case 'audit':
          return renderAuditLog()

        case 'saved':
          return renderSavedAccounts()

        case 'chat-ai':
          return renderChat()

        case 'api-explorer':
          return renderApiExplorer()

        default:
          return renderHome()
      }
    }

    // Marketing views (only when not AI)
    if (!isAi) {
      switch (activeNav) {
      case 'campaign-control':
        if (state.loading) return renderLoading()
        if (flowState === 5) return renderMarketingPreview()
        if (isComplete) return renderCompleted()
        return renderHome()

      case 'market-intel':
        return (
          <Box>
            <Typography variant="h6" sx={{ color: '#e8eaed', mb: 2, fontSize: 15, fontWeight: 600 }}>
              <SearchIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-top' }} />
              Market Intelligence
            </Typography>
            <SearchResults
              results={state.searchResults}
              loading={state.searchLoading}
              onSearch={search}
              onAddToPipeline={handleAddToPipeline}
              addedIds={pipelineAddedIds}
            />
          </Box>
        )

      case 'content-library':
        return renderContentLibrary()

      case 'live-pipelines':
        return renderLivePipelines()

      case 'automation-rules':
        return renderAutomationRules()

      case 'chat-ai':
        return renderChat()

      case 'api-explorer':
        return renderApiExplorer()

      default:
        return renderHome()
      }
    }

    // AI mode
    if (isAi) {
      switch (activeNav) {
        case 'ai-home':
          return renderAiHome()
        case 'rag-console':
          return renderRagConsole()
        case 'memory-vault':
          return renderMemoryVault()
        case 'evaluation-lab':
          return renderEvaluationLab()
        case 'doc-manager':
          return renderDocumentManager()
        case 'chat-ai':
          return renderChat()
        case 'api-explorer':
          return renderApiExplorer()
        default:
          return renderAiHome()
      }
    }
  }

  return (
    <CopilotLayout
      mode={state.mode}
      onModeChange={handleModeChange}
      activeNav={activeNav}
      onNavChange={handleNavChange}
      loading={state.loading}
    >
      {/* Error Banner */}
      {state.error && (
        <Box sx={{
          background: 'rgba(255,68,68,0.1)',
          border: '1px solid rgba(255,68,68,0.3)',
          borderRadius: '6px',
          p: 2,
          mb: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <Typography variant="body2" color="#ff4444">{state.error}</Typography>
          <Button
            size="small"
            onClick={dismissError}
            sx={{ color: '#ff4444', minWidth: 'auto', p: '2px 8px', fontSize: 12 }}
          >
            Dismiss
          </Button>
        </Box>
      )}

      {renderMainContent()}

      {/* Approval Overlay (State 6) — rendered on top of workspace */}
      {renderApprovalOverlay()}
    </CopilotLayout>
  )
}
