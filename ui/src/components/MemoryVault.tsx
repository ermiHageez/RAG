import { useState } from 'react'
import { Box, Typography, TextField, Button, Chip, CircularProgress } from '@mui/material'
import MemoryIcon from '@mui/icons-material/Memory'
import { getMemory, saveMemory } from '../api/memory'

const memoryTypes = ['conversation', 'custom']

export default function MemoryVault() {
  const [memoryType, setMemoryType] = useState('conversation')
  const [content, setContent] = useState('')
  const [role, setRole] = useState('user')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFetch = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getMemory(memoryType)
      setResult(JSON.stringify(data, null, 2))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fetch failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!content.trim()) return
    setLoading(true)
    setError(null)
    try {
      const data = await saveMemory(memoryType, { role, content })
      setResult(JSON.stringify(data, null, 2))
      setContent('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <MemoryIcon sx={{ color: '#00c853', fontSize: 20 }} />
        <Typography variant="h6" sx={{ color: '#e8eaed', fontSize: 15, fontWeight: 600 }}>
          Memory Vault
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 0.5, mb: 2 }}>
        {memoryTypes.map(t => (
          <Chip
            key={t}
            label={t.charAt(0).toUpperCase() + t.slice(1)}
            size="small"
            onClick={() => { setMemoryType(t); setResult(null) }}
            sx={{
              background: memoryType === t ? 'rgba(0,200,83,0.15)' : 'rgba(255,255,255,0.06)',
              color: memoryType === t ? '#00c853' : '#9aa0a6',
              border: `1px solid ${memoryType === t ? 'rgba(0,200,83,0.3)' : 'rgba(255,255,255,0.08)'}`,
              cursor: 'pointer',
            }}
          />
        ))}
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Button
          variant="outlined"
          onClick={handleFetch}
          disabled={loading}
          sx={{ color: '#00c853', borderColor: 'rgba(0,200,83,0.3)' }}
        >
          {loading ? <CircularProgress size={14} /> : `Get ${memoryType} Memory`}
        </Button>
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
        <Chip
          label="Role: user"
          size="small"
          onClick={() => setRole('user')}
          sx={{
            background: role === 'user' ? 'rgba(0,200,83,0.15)' : 'rgba(255,255,255,0.06)',
            color: role === 'user' ? '#00c853' : '#9aa0a6',
            cursor: 'pointer',
          }}
        />
        <Chip
          label="Role: assistant"
          size="small"
          onClick={() => setRole('assistant')}
          sx={{
            background: role === 'assistant' ? 'rgba(0,200,83,0.15)' : 'rgba(255,255,255,0.06)',
            color: role === 'assistant' ? '#00c853' : '#9aa0a6',
            cursor: 'pointer',
          }}
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField
          size="small"
          fullWidth
          placeholder="Memory content..."
          value={content}
          onChange={e => setContent(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleSave() }}
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
          onClick={handleSave}
          disabled={loading || !content.trim()}
          sx={{ background: '#00c853', color: '#121214', fontWeight: 600, '&:hover': { background: '#00e676' } }}
        >
          {loading ? <CircularProgress size={16} sx={{ color: '#121214' }} /> : 'Save'}
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
