import { useState, useEffect, useRef } from 'react'
import { Box, Typography, Button, Chip, CircularProgress, Alert } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import RefreshIcon from '@mui/icons-material/Refresh'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import StorageIcon from '@mui/icons-material/Storage'
import { uploadRagFile, getRagStatus, rebuildRag } from '../api/rag'

export default function RagConsole() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const [uploading, setUploading] = useState(false)

  const [rebuildLoading, setRebuildLoading] = useState(false)
  const [rebuildMsg, setRebuildMsg] = useState<string | null>(null)

  const [status, setStatus] = useState<{ active: boolean; entries: number; dimension: number } | null>(null)
  const [statusLoading, setStatusLoading] = useState(false)

  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    if (file && !file.name.endsWith('.txt')) {
      setError('Only .txt files allowed')
      return
    }
    setSelectedFile(file)
    setError(null)
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    setUploading(true)
    setError(null)
    try {
      const data = await uploadRagFile(selectedFile)
      setUploadedFiles(prev => [...prev, data.path])
      setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleRebuild = async () => {
    setRebuildLoading(true)
    setError(null)
    setRebuildMsg(null)
    try {
      const data = await rebuildRag()
      setRebuildMsg(JSON.stringify(data, null, 2))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rebuild failed')
    } finally {
      setRebuildLoading(false)
    }
  }

  const handleStatus = async () => {
    setStatusLoading(true)
    setError(null)
    try {
      const data = await getRagStatus()
      setStatus({ active: data.active, entries: data.entries, dimension: data.dimension })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Status check failed')
    } finally {
      setStatusLoading(false)
    }
  }

  useEffect(() => { handleStatus() }, [])

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <StorageIcon sx={{ color: '#00c853', fontSize: 20 }} />
        <Typography variant="h6" sx={{ color: '#e8eaed', fontSize: 15, fontWeight: 600 }}>
          RAG Console
        </Typography>
      </Box>

      {/* STEP 1 — Upload .txt file */}
      <Box sx={{ p: 2, background: '#1a1a1e', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '4px', mb: 2 }}>
        <Typography variant="body2" sx={{ color: '#e8eaed', fontWeight: 600, mb: 1.5 }}>
          1. Upload a .txt file to <code style={{ color: '#00c853' }}>data/</code>
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <Button
            variant="outlined"
            size="small"
            startIcon={<CloudUploadIcon />}
            onClick={() => fileInputRef.current?.click()}
            sx={{ color: '#9aa0a6', borderColor: 'rgba(255,255,255,0.12)' }}
          >
            {selectedFile ? selectedFile.name : 'Choose .txt file'}
          </Button>
          <Button
            variant="contained"
            size="small"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            sx={{ background: '#00c853', color: '#121214', fontWeight: 600, '&:hover': { background: '#00e676' } }}
          >
            {uploading ? <CircularProgress size={14} sx={{ color: '#121214' }} /> : 'Upload'}
          </Button>
        </Box>
        {uploadedFiles.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" color="#5f6368">Uploaded files:</Typography>
            {uploadedFiles.map((f, i) => (
              <Typography key={i} variant="caption" sx={{ color: '#00c853', display: 'block', fontFamily: 'monospace', fontSize: 11 }}>
                ✓ {f}
              </Typography>
            ))}
          </Box>
        )}
      </Box>

      {/* STEP 2 — Reload RAG */}
      <Box sx={{ p: 2, background: '#1a1a1e', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '4px', mb: 2 }}>
        <Typography variant="body2" sx={{ color: '#e8eaed', fontWeight: 600, mb: 1.5 }}>
          2. Reload RAG (rebuild vector store from <code style={{ color: '#ff9100' }}>data/</code>)
        </Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={handleRebuild}
          disabled={rebuildLoading}
          sx={{ background: '#ff9100', color: '#000', fontWeight: 600, '&:hover': { background: '#ffab00' } }}
        >
          {rebuildLoading ? <CircularProgress size={14} sx={{ color: '#000' }} /> : 'Reload RAG'}
        </Button>
        {rebuildMsg && (
          <Box
            component="pre"
            sx={{
              color: '#e8eaed',
              fontSize: 11,
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              m: 0,
              mt: 1,
              maxHeight: 120,
              overflow: 'auto',
            }}
          >
            {rebuildMsg}
          </Box>
        )}
      </Box>

      {/* STEP 3 — Check Status */}
      <Box sx={{ p: 2, background: '#1a1a1e', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '4px' }}>
        <Typography variant="body2" sx={{ color: '#e8eaed', fontWeight: 600, mb: 1.5 }}>
          3. Check vector store status
        </Typography>
        <Button
          variant="outlined"
          startIcon={<CheckCircleIcon />}
          onClick={handleStatus}
          disabled={statusLoading}
          sx={{ color: '#00c853', borderColor: 'rgba(0,200,83,0.3)' }}
        >
          {statusLoading ? <CircularProgress size={14} sx={{ color: '#00c853' }} /> : 'Check Status'}
        </Button>
        {status && (
          <Box sx={{ display: 'flex', gap: 1, mt: 1.5, flexWrap: 'wrap' }}>
            <Chip label={`Status: ${status.active ? 'Active' : 'Inactive'}`} size="small" sx={{ color: status.active ? '#00c853' : '#ff4444', background: status.active ? 'rgba(0,200,83,0.1)' : 'rgba(255,68,68,0.1)', fontWeight: 600 }} />
            <Chip label={`Documents: ${status.entries}`} size="small" sx={{ color: '#9aa0a6', background: 'rgba(255,255,255,0.06)' }} />
            <Chip label={`Dimension: ${status.dimension}`} size="small" sx={{ color: '#9aa0a6', background: 'rgba(255,255,255,0.06)' }} />
          </Box>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 2, background: 'rgba(255,68,68,0.1)', color: '#ff4444', border: '1px solid rgba(255,68,68,0.3)', '& .MuiAlertIcon-root': { color: '#ff4444' } }}>
          {error}
        </Alert>
      )}
    </Box>
  )
}
