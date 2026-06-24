import { useState } from 'react'
import { Box, Typography, TextField, Button, Chip, CircularProgress } from '@mui/material'
import BuildIcon from '@mui/icons-material/Build'
import { listMcpTools, mcpTenders, mcpDirectory } from '../api/tools'

const actions = [
  { key: 'tools', label: 'List Tools', color: '#00c853' },
  { key: 'tenders', label: 'Search Tenders', color: '#2979ff' },
  { key: 'directory', label: 'Company Directory', color: '#ff9100' },
]

export default function McpToolbox() {
  const [activeAction, setActiveAction] = useState('tools')
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleRun = async () => {
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      let data: unknown
      switch (activeAction) {
        case 'tools':
          data = await listMcpTools()
          break
        case 'tenders':
          if (!query.trim()) { setError('Enter a search query'); setLoading(false); return }
          data = await mcpTenders(query)
          break
        case 'directory':
          if (!query.trim()) { setError('Enter a sector'); setLoading(false); return }
          data = await mcpDirectory(query)
          break
      }
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
        <BuildIcon sx={{ color: '#00c853', fontSize: 20 }} />
        <Typography variant="h6" sx={{ color: '#e8eaed', fontSize: 15, fontWeight: 600 }}>
          MCP Toolbox
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 0.5, mb: 2, flexWrap: 'wrap' }}>
        {actions.map(a => (
          <Chip
            key={a.key}
            label={a.label}
            size="small"
            onClick={() => { setActiveAction(a.key); setResult(null); setError(null) }}
            sx={{
              background: activeAction === a.key ? `${a.color}18` : 'rgba(255,255,255,0.06)',
              color: activeAction === a.key ? a.color : '#9aa0a6',
              border: `1px solid ${activeAction === a.key ? `${a.color}4d` : 'rgba(255,255,255,0.08)'}`,
              cursor: 'pointer',
            }}
          />
        ))}
      </Box>

      {activeAction !== 'tools' && (
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <TextField
            size="small"
            fullWidth
            placeholder={activeAction === 'tenders' ? 'Search tenders...' : 'Sector name...'}
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
            disabled={loading}
            sx={{ background: '#00c853', color: '#121214', fontWeight: 600, '&:hover': { background: '#00e676' }, minWidth: 80 }}
          >
            {loading ? <CircularProgress size={16} sx={{ color: '#121214' }} /> : 'Go'}
          </Button>
        </Box>
      )}

      {activeAction === 'tools' && (
        <Button
          variant="contained"
          onClick={handleRun}
          disabled={loading}
          sx={{ background: '#00c853', color: '#121214', fontWeight: 600, '&:hover': { background: '#00e676' }, mb: 2 }}
        >
          {loading ? <CircularProgress size={16} sx={{ color: '#121214' }} /> : 'Fetch Tools'}
        </Button>
      )}

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
