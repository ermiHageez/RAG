import { useState } from 'react'
import { Box, Typography, TextField, Button, CircularProgress } from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import { downloadDocument } from '../api/documents'

export default function DocumentManager() {
  const [sessionId, setSessionId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [downloaded, setDownloaded] = useState(false)

  const handleDownload = async () => {
    if (!sessionId.trim()) return
    setLoading(true)
    setError(null)
    setDownloaded(false)
    try {
      const blob = await downloadDocument(sessionId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `proposal-${sessionId}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      setDownloaded(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <DescriptionIcon sx={{ color: '#00c853', fontSize: 20 }} />
        <Typography variant="h6" sx={{ color: '#e8eaed', fontSize: 15, fontWeight: 600 }}>
          Document Manager
        </Typography>
      </Box>
      <Typography variant="body2" color="#9aa0a6" sx={{ mb: 2 }}>
        Download generated proposal PDFs by session ID.
      </Typography>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField
          size="small"
          fullWidth
          placeholder="Session ID..."
          value={sessionId}
          onChange={e => setSessionId(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleDownload() }}
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
          onClick={handleDownload}
          disabled={loading || !sessionId.trim()}
          sx={{ background: '#00c853', color: '#121214', fontWeight: 600, '&:hover': { background: '#00e676' }, minWidth: 120 }}
        >
          {loading ? <CircularProgress size={16} sx={{ color: '#121214' }} /> : 'Download PDF'}
        </Button>
      </Box>

      {error && (
        <Box sx={{ p: 2, background: 'rgba(255,68,68,0.1)', border: '1px solid rgba(255,68,68,0.3)', borderRadius: '4px', mb: 2 }}>
          <Typography variant="body2" color="#ff4444">{error}</Typography>
        </Box>
      )}

      {downloaded && (
        <Box sx={{ p: 2, background: 'rgba(0,200,83,0.1)', border: '1px solid rgba(0,200,83,0.3)', borderRadius: '4px' }}>
          <Typography variant="body2" color="#00c853">Download started!</Typography>
        </Box>
      )}
    </Box>
  )
}
