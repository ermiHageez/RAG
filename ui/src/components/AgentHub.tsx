import { useState } from 'react'
import { Box, Typography, TextField, Button, Chip, CircularProgress } from '@mui/material'
import PsychologyIcon from '@mui/icons-material/Psychology'
import { runAgent, runSupervisor, searchLeads, searchTenders, knowledgeSearch, salesIntelligence, draftContent, runApproval } from '../api/agent'

const agents = [
  { key: 'full', label: 'Full Agent', api: runAgent },
  { key: 'supervisor', label: 'Supervisor', api: (q: string) => runSupervisor(q) },
  { key: 'leads', label: 'Lead Search', api: (q: string) => searchLeads(q) },
  { key: 'tenders', label: 'Tender Search', api: (q: string) => searchTenders(q) },
  { key: 'knowledge', label: 'Knowledge', api: (q: string) => knowledgeSearch(q) },
  { key: 'sales-intel', label: 'Sales Intel', api: (q: string) => salesIntelligence(q) },
  { key: 'content', label: 'Content Draft', api: (q: string) => draftContent(q) },
  { key: 'approval', label: 'Approval', api: (q: string) => runApproval(q) },
]

export default function AgentHub() {
  const [query, setQuery] = useState('')
  const [activeAgent, setActiveAgent] = useState('full')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleRun = async () => {
    if (!query.trim()) return
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const agent = agents.find(a => a.key === activeAgent)!
      const data = await agent.api(query)
      setResult(JSON.stringify(data, null, 2))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <PsychologyIcon sx={{ color: '#00c853', fontSize: 20 }} />
        <Typography variant="h6" sx={{ color: '#e8eaed', fontSize: 15, fontWeight: 600 }}>
          Agent Hub
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 0.5, mb: 2, flexWrap: 'wrap' }}>
        {agents.map(a => (
          <Chip
            key={a.key}
            label={a.label}
            size="small"
            onClick={() => setActiveAgent(a.key)}
            sx={{
              background: activeAgent === a.key ? 'rgba(0,200,83,0.15)' : 'rgba(255,255,255,0.06)',
              color: activeAgent === a.key ? '#00c853' : '#9aa0a6',
              border: `1px solid ${activeAgent === a.key ? 'rgba(0,200,83,0.3)' : 'rgba(255,255,255,0.08)'}`,
              cursor: 'pointer',
            }}
          />
        ))}
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField
          size="small"
          fullWidth
          placeholder={`Enter query for ${agents.find(a => a.key === activeAgent)?.label}...`}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleRun() }}
          sx={{
            '& .MuiOutlinedInput-root': {
              background: '#1a1a1e',
              color: '#e8eaed',
              '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' },
              '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
            },
          }}
        />
        <Button
          variant="contained"
          onClick={handleRun}
          disabled={loading || !query.trim()}
          sx={{ background: '#00c853', color: '#121214', fontWeight: 600, '&:hover': { background: '#00e676' }, minWidth: 80 }}
        >
          {loading ? <CircularProgress size={16} sx={{ color: '#121214' }} /> : 'Run'}
        </Button>
      </Box>

      {error && (
        <Box sx={{ p: 2, background: 'rgba(255,68,68,0.1)', border: '1px solid rgba(255,68,68,0.3)', borderRadius: '4px', mb: 2 }}>
          <Typography variant="body2" color="#ff4444">{error}</Typography>
        </Box>
      )}

      {result && (
        <Box sx={{ p: 2, background: '#1a1a1e', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '4px' }}>
          <Typography variant="caption" color="#9aa0a6" sx={{ mb: 1, display: 'block' }}>Response:</Typography>
          <Box
            component="pre"
            sx={{
              color: '#e8eaed',
              fontSize: 11,
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              m: 0,
              maxHeight: 400,
              overflow: 'auto',
            }}
          >
            {result}
          </Box>
        </Box>
      )}
    </Box>
  )
}
