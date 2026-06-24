import { Box, Typography, Card, CardContent } from '@mui/material'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import StorageIcon from '@mui/icons-material/Storage'
import MemoryIcon from '@mui/icons-material/Memory'
import ScienceIcon from '@mui/icons-material/Science'
import DescriptionIcon from '@mui/icons-material/Description'
import ChatIcon from '@mui/icons-material/Chat'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'

interface AiHubProps {
  onNavigate: (key: string) => void
}

const cards = [
  { key: 'rag-console', label: 'RAG Console', icon: <StorageIcon sx={{ fontSize: 32 }} />, desc: 'View vector store status, rebuild from .txt files' },
  { key: 'memory-vault', label: 'Memory Vault', icon: <MemoryIcon sx={{ fontSize: 32 }} />, desc: 'View and save conversation & custom memory' },
  { key: 'evaluation-lab', label: 'Evaluation Lab', icon: <ScienceIcon sx={{ fontSize: 32 }} />, desc: 'Run RAG, routing, and content evaluations' },
  { key: 'doc-manager', label: 'Document Manager', icon: <DescriptionIcon sx={{ fontSize: 32 }} />, desc: 'Download generated proposals' },
  { key: 'chat-ai', label: 'AI Chat', icon: <ChatIcon sx={{ fontSize: 32 }} />, desc: 'Chat with RAG or use /commands to call any endpoint' },
  { key: 'api-explorer', label: 'API Explorer', icon: <HelpOutlineIcon sx={{ fontSize: 32 }} />, desc: 'Browse all available API endpoints' },
]

export default function AiHub({ onNavigate }: AiHubProps) {
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <SmartToyIcon sx={{ color: '#00c853', fontSize: 28 }} />
        <Typography variant="h6" sx={{ color: '#e8eaed', fontWeight: 600, fontSize: 18 }}>
          AI Mode Hub
        </Typography>
      </Box>
      <Typography variant="body2" color="#9aa0a6" sx={{ mb: 3 }}>
        Explore all AI-powered tools. Click a card to get started, or use the sidebar navigation.
      </Typography>

      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 2 }}>
        {cards.map(card => (
          <Card
            key={card.key}
            onClick={() => onNavigate(card.key)}
            sx={{
              background: '#1a1a1e',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '6px',
              cursor: 'pointer',
              transition: 'all 0.12s ease',
              '&:hover': {
                borderColor: 'rgba(0,200,83,0.3)',
                background: 'rgba(0,200,83,0.04)',
                transform: 'translateY(-1px)',
              },
            }}
          >
            <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                <Box sx={{ color: '#00c853' }}>{card.icon}</Box>
                <Typography variant="body1" sx={{ color: '#e8eaed', fontWeight: 600, fontSize: 14 }}>
                  {card.label}
                </Typography>
              </Box>
              <Typography variant="body2" color="#9aa0a6" sx={{ fontSize: 12 }}>
                {card.desc}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  )
}
