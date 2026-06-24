import { useState } from 'react'
import { Box, Typography, Button, Chip, CircularProgress } from '@mui/material'
import ScienceIcon from '@mui/icons-material/Science'
import { evaluateRag, evaluateRouting, evaluateContent } from '../api/evaluate'

const evals = [
  { key: 'rag', label: 'RAG Precision', api: evaluateRag, color: '#00c853' },
  { key: 'routing', label: 'Routing Accuracy', api: evaluateRouting, color: '#2979ff' },
  { key: 'content', label: 'Content Quality', api: evaluateContent, color: '#ff9100' },
]

export default function EvaluationLab() {
  const [running, setRunning] = useState<string | null>(null)
  const [results, setResults] = useState<Record<string, string>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleRun = async (key: string, api: () => Promise<unknown>) => {
    setRunning(key)
    setErrors(prev => ({ ...prev, [key]: '' }))
    try {
      const data = await api()
      setResults(prev => ({ ...prev, [key]: JSON.stringify(data, null, 2) }))
    } catch (err) {
      setErrors(prev => ({ ...prev, [key]: err instanceof Error ? err.message : 'Evaluation failed' }))
    } finally {
      setRunning(null)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <ScienceIcon sx={{ color: '#00c853', fontSize: 20 }} />
        <Typography variant="h6" sx={{ color: '#e8eaed', fontSize: 15, fontWeight: 600 }}>
          Evaluation Lab
        </Typography>
      </Box>
      <Typography variant="body2" color="#9aa0a6" sx={{ mb: 2 }}>
        Run benchmark evaluations to measure system performance.
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {evals.map(e => (
          <Box key={e.key} sx={{ p: 2, background: '#1a1a1e', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '4px' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip label={e.label} size="small" sx={{ background: `${e.color}18`, color: e.color, fontWeight: 600 }} />
              </Box>
              <Button
                variant="outlined"
                size="small"
                onClick={() => handleRun(e.key, e.api)}
                disabled={running === e.key}
                sx={{ color: e.color, borderColor: `${e.color}4d` }}
              >
                {running === e.key ? <CircularProgress size={14} /> : 'Run'}
              </Button>
            </Box>
            {errors[e.key] && (
              <Typography variant="body2" color="#ff4444" sx={{ fontSize: 12 }}>{errors[e.key]}</Typography>
            )}
            {results[e.key] && (
              <Box
                component="pre"
                sx={{
                  color: '#e8eaed',
                  fontSize: 11,
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  m: 0,
                  maxHeight: 200,
                  overflow: 'auto',
                  mt: 1,
                }}
              >
                {results[e.key]}
              </Box>
            )}
          </Box>
        ))}
      </Box>
    </Box>
  )
}
