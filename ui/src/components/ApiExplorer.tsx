import { useState } from 'react'
import { Box, Typography, TextField, Chip } from '@mui/material'
import type { EndpointInfo } from '../types'

const endpoints: EndpointInfo[] = [
  { method: 'GET', path: '/health', description: 'API health status', section: 'Health', access: 'page' },
  { method: 'GET', path: '/config', description: 'App configuration', section: 'Health', access: 'page' },
  { method: 'POST', path: '/agent/run', description: 'Run full multi-agent graph', section: 'Agent', access: 'both', command: '/run-agent <query>' },
  { method: 'POST', path: '/agent/supervisor', description: 'Run supervisor agent for routing', section: 'Agent', access: 'command', command: '/supervisor <query>' },
  { method: 'POST', path: '/agent/leads', description: 'Lead search agent', section: 'Agent', access: 'command', command: '/search-leads <query>' },
  { method: 'POST', path: '/agent/tenders', description: 'Tender search agent', section: 'Agent', access: 'command', command: '/search-tenders <query>' },
  { method: 'POST', path: '/agent/knowledge', description: 'Knowledge retrieval agent', section: 'Agent', access: 'command', command: '/knowledge <query>' },
  { method: 'POST', path: '/agent/sales-intel', description: 'Sales intelligence agent', section: 'Agent', access: 'command', command: '/sales-intel <query>' },
  { method: 'POST', path: '/agent/content', description: 'Content drafting agent', section: 'Agent', access: 'command', command: '/draft-content <topic>' },
  { method: 'POST', path: '/agent/approval', description: 'Approval agent', section: 'Agent', access: 'command', command: '/approve <id>' },
  { method: 'GET', path: '/rag/status', description: 'FAISS vector store status', section: 'RAG', access: 'both', command: '/rag-status' },
  { method: 'POST', path: '/rag/query', description: 'Query vector store', section: 'RAG', access: 'both', command: '/rag-query <query>' },
  { method: 'POST', path: '/rag/rebuild', description: 'Rebuild vector store', section: 'RAG', access: 'both', command: '/rag-rebuild' },
  { method: 'POST', path: '/rag/chat', description: 'Chat with RAG context', section: 'RAG', access: 'page' },
  { method: 'GET', path: '/mcp/tools', description: 'List MCP search tools', section: 'MCP', access: 'both', command: '/mcp-tools' },
  { method: 'POST', path: '/mcp/search', description: 'Search Ethiopian enterprises', section: 'MCP', access: 'page' },
  { method: 'POST', path: '/mcp/tenders', description: 'Fetch active tenders', section: 'MCP', access: 'both', command: '/tenders <query>' },
  { method: 'POST', path: '/mcp/directory', description: 'Discover companies from directories', section: 'MCP', access: 'both', command: '/directory <sector>' },
  { method: 'GET', path: '/memory/{memory_type}', description: 'Get memory history', section: 'Memory', access: 'both', command: '/memory <type>' },
  { method: 'POST', path: '/memory/{memory_type}', description: 'Save memory interaction', section: 'Memory', access: 'command', command: '/remember <key>:<value>' },
  { method: 'POST', path: '/evaluate/rag', description: 'RAG precision benchmark', section: 'Evaluation', access: 'both', command: '/eval-rag' },
  { method: 'POST', path: '/evaluate/routing', description: 'Agent routing accuracy', section: 'Evaluation', access: 'both', command: '/eval-routing' },
  { method: 'POST', path: '/evaluate/content', description: 'Content quality evaluation', section: 'Evaluation', access: 'both', command: '/eval-content' },
  { method: 'POST', path: '/sales/start', description: 'Create new sales session', section: 'Sales', access: 'command', command: '/new-deal' },
  { method: 'POST', path: '/sales/chat', description: 'Chat in sales session', section: 'Sales', access: 'page' },
  { method: 'POST', path: '/sales/generate', description: 'Generate proposal PDF', section: 'Sales', access: 'command', command: '/generate-proposal' },
  { method: 'POST', path: '/sales/approve-send', description: 'Approve & send proposal', section: 'Sales', access: 'command', command: '/approve-send' },
  { method: 'POST', path: '/sales/reset', description: 'Reset sales session', section: 'Sales', access: 'command', command: '/reset-session' },
  { method: 'GET', path: '/doc-gen/download/{session_id}', description: 'Download proposal PDF', section: 'Doc Gen', access: 'both', command: '/download-proposal <id>' },
  { method: 'GET', path: '/marketing/templates', description: 'List email templates', section: 'Marketing', access: 'page' },
  { method: 'GET', path: '/marketing/templates/{product}', description: 'Get template HTML', section: 'Marketing', access: 'command', command: '/get-template <product>' },
  { method: 'PUT', path: '/marketing/templates/{product}', description: 'Update template HTML', section: 'Marketing', access: 'command', command: '/update-template <product>' },
  { method: 'GET', path: '/marketing/campaign/stats', description: 'Campaign statistics', section: 'Marketing', access: 'page' },
  { method: 'GET', path: '/marketing/campaign/leads', description: 'Campaign leads', section: 'Marketing', access: 'command', command: '/campaign-leads' },
  { method: 'PUT', path: '/marketing/campaign/leads/{session_id}/status', description: 'Update lead status', section: 'Marketing', access: 'command', command: '/update-lead-status <id> <status>' },
  { method: 'POST', path: '/marketing/follow-up/check', description: 'Send due follow-ups', section: 'Marketing', access: 'command', command: '/check-followups' },
  { method: 'GET', path: '/marketing/follow-up/schedule/{session_id}', description: 'Follow-up schedule', section: 'Marketing', access: 'command', command: '/followup-schedule <id>' },
  { method: 'GET', path: '/marketing/follow-up/config', description: 'Get follow-up config', section: 'Marketing', access: 'page' },
  { method: 'PUT', path: '/marketing/follow-up/config', description: 'Update follow-up config', section: 'Marketing', access: 'command', command: '/update-followup-config' },
  { method: 'GET', path: '/marketing/analytics/summary', description: 'Analytics summary', section: 'Marketing', access: 'page' },
  { method: 'GET', path: '/marketing/analytics/product-breakdown', description: 'Product breakdown', section: 'Marketing', access: 'command', command: '/analytics-products' },
  { method: 'GET', path: '/marketing/analytics/timeline', description: 'Timeline data', section: 'Marketing', access: 'command', command: '/analytics-timeline' },
  { method: 'GET', path: '/marketing/analytics/export', description: 'Export analytics report', section: 'Marketing', access: 'command', command: '/export-analytics' },
  { method: 'POST', path: '/copilot/run', description: 'Run copilot pipeline', section: 'Copilot', access: 'page' },
  { method: 'POST', path: '/copilot/review', description: 'Review/approve a step', section: 'Copilot', access: 'command', command: '/review-step <id> <action>' },
  { method: 'POST', path: '/copilot/approve-send', description: 'Approve & send email', section: 'Copilot', access: 'page' },
  { method: 'GET', path: '/copilot/session/{session_id}', description: 'Get session details', section: 'Copilot', access: 'command', command: '/session <id>' },
  { method: 'GET', path: '/copilot/explain/{session_id}/{step}', description: 'Get step explanation', section: 'Copilot', access: 'command', command: '/explain <id> <step>' },
]

const methodColors: Record<string, string> = {
  GET: '#00c853',
  POST: '#2979ff',
  PUT: '#ff9100',
  DELETE: '#ff1744',
}

const accessColors: Record<string, string> = {
  page: '#2979ff',
  command: '#ff9100',
  both: '#00c853',
}

export default function ApiExplorer() {
  const [search, setSearch] = useState('')
  const [sectionFilter, setSectionFilter] = useState<string>('')

  const sections = [...new Set(endpoints.map(e => e.section))].sort()

  const filtered = endpoints.filter(e => {
    const matchSearch = !search || e.path.toLowerCase().includes(search.toLowerCase()) || e.description.toLowerCase().includes(search.toLowerCase())
    const matchSection = !sectionFilter || e.section === sectionFilter
    return matchSearch && matchSection
  })

  const handleCopy = (path: string) => {
    navigator.clipboard.writeText(path)
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ color: '#e8eaed', mb: 2, fontSize: 15, fontWeight: 600 }}>
        API Endpoint Explorer
      </Typography>
      <Typography variant="body2" color="#9aa0a6" sx={{ mb: 2 }}>
        Reference for all available backend endpoints. Use the search bar or filter by section.
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <TextField
          size="small"
          placeholder="Search endpoints..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          sx={{
            minWidth: 280,
            '& .MuiOutlinedInput-root': {
              background: '#1a1a1e',
              color: '#e8eaed',
              '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' },
              '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
            },
          }}
        />
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', alignItems: 'center' }}>
          <Chip
            label="All"
            size="small"
            onClick={() => setSectionFilter('')}
            sx={{
              background: !sectionFilter ? 'rgba(0,200,83,0.15)' : 'rgba(255,255,255,0.06)',
              color: !sectionFilter ? '#00c853' : '#9aa0a6',
              border: `1px solid ${!sectionFilter ? 'rgba(0,200,83,0.3)' : 'rgba(255,255,255,0.08)'}`,
              cursor: 'pointer',
            }}
          />
          {sections.map(s => (
            <Chip
              key={s}
              label={s}
              size="small"
              onClick={() => setSectionFilter(s === sectionFilter ? '' : s)}
              sx={{
                background: sectionFilter === s ? 'rgba(0,200,83,0.15)' : 'rgba(255,255,255,0.06)',
                color: sectionFilter === s ? '#00c853' : '#9aa0a6',
                border: `1px solid ${sectionFilter === s ? 'rgba(0,200,83,0.3)' : 'rgba(255,255,255,0.08)'}`,
                cursor: 'pointer',
              }}
            />
          ))}
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {filtered.map((ep, i) => (
          <Box
            key={i}
            onClick={() => handleCopy(ep.path)}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              p: '8px 12px',
              background: '#1a1a1e',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: '4px',
              cursor: 'pointer',
              transition: 'all 0.12s ease',
              '&:hover': { borderColor: 'rgba(0,200,83,0.3)', background: 'rgba(0,200,83,0.04)' },
              '&:active': { background: 'rgba(0,200,83,0.1)' },
            }}
            title="Click to copy path"
          >
            <Chip
              label={ep.method}
              size="small"
              sx={{
                background: `${methodColors[ep.method]}18`,
                color: methodColors[ep.method],
                fontWeight: 600,
                fontSize: 10,
                minWidth: 52,
                fontFamily: 'monospace',
              }}
            />
            <Typography
              variant="body2"
              sx={{ color: '#e8eaed', fontFamily: 'monospace', fontSize: 12, flex: 1 }}
            >
              {ep.path}
            </Typography>
            <Typography variant="body2" sx={{ color: '#9aa0a6', fontSize: 11, flex: 1, maxWidth: 300 }}>
              {ep.description}
            </Typography>
            <Chip
              label={ep.access === 'both' ? 'Page + /command' : ep.access === 'page' ? 'Page' : '/command'}
              size="small"
              sx={{
                background: `${accessColors[ep.access]}18`,
                color: accessColors[ep.access],
                fontSize: 10,
              }}
            />
            {ep.command && (
              <Typography variant="body2" sx={{ color: '#5f6368', fontFamily: 'monospace', fontSize: 11 }}>
                {ep.command}
              </Typography>
            )}
          </Box>
        ))}
      </Box>

      {filtered.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="body2" color="#5f6368">No endpoints match your filter.</Typography>
        </Box>
      )}

      <Box sx={{ mt: 2, textAlign: 'right' }}>
        <Typography variant="caption" color="#5f6368">
          {filtered.length} of {endpoints.length} endpoints shown
        </Typography>
      </Box>
    </Box>
  )
}
