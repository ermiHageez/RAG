import { type ReactNode } from 'react'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import ExploreIcon from '@mui/icons-material/Explore'
import SearchIcon from '@mui/icons-material/Search'
import TrackChangesIcon from '@mui/icons-material/TrackChanges'
import BarChartIcon from '@mui/icons-material/BarChart'
import TimelineIcon from '@mui/icons-material/Timeline'
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder'
import ChatIcon from '@mui/icons-material/Chat'
import DashboardIcon from '@mui/icons-material/Dashboard'
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks'
import CampaignIcon from '@mui/icons-material/Campaign'
import SettingsIcon from '@mui/icons-material/Settings'
import StorageIcon from '@mui/icons-material/Storage'
import MemoryIcon from '@mui/icons-material/Memory'
import ScienceIcon from '@mui/icons-material/Science'
import DescriptionIcon from '@mui/icons-material/Description'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import styles from './CopilotLayout.module.css'

interface NavItem {
  key: string
  label: string
  icon: ReactNode
}

const salesNav: NavItem[] = [
  { key: 'home', label: 'Co-Pilot Home', icon: <ExploreIcon /> },
  { key: 'search', label: 'Deep Account Search', icon: <SearchIcon /> },
  { key: 'deal-board', label: 'Active Deal Board', icon: <TrackChangesIcon /> },
  { key: 'metrics', label: 'Performance Metrics', icon: <BarChartIcon /> },
  { key: 'audit', label: 'System Audit Log', icon: <TimelineIcon /> },
  { key: 'saved', label: 'Saved Accounts', icon: <BookmarkBorderIcon /> },
  { key: 'chat-ai', label: 'AI Chat', icon: <ChatIcon /> },
]

const marketingNav: NavItem[] = [
  { key: 'campaign-control', label: 'Campaign Control', icon: <DashboardIcon /> },
  { key: 'market-intel', label: 'Market Intelligence', icon: <SearchIcon /> },
  { key: 'content-library', label: 'Content Library', icon: <LibraryBooksIcon /> },
  { key: 'live-pipelines', label: 'Live Pipelines', icon: <CampaignIcon /> },
  { key: 'automation-rules', label: 'Automation Rules', icon: <SettingsIcon /> },
  { key: 'chat-ai', label: 'AI Chat', icon: <ChatIcon /> },
]

const aiNav: NavItem[] = [
  { key: 'ai-home', label: 'AI Hub', icon: <SmartToyIcon /> },
  { key: 'rag-console', label: 'RAG Console', icon: <StorageIcon /> },
  { key: 'memory-vault', label: 'Memory Vault', icon: <MemoryIcon /> },
  { key: 'evaluation-lab', label: 'Evaluation Lab', icon: <ScienceIcon /> },
  { key: 'doc-manager', label: 'Document Manager', icon: <DescriptionIcon /> },
  { key: 'chat-ai', label: 'AI Chat', icon: <ChatIcon /> },
]

interface CopilotLayoutProps {
  children: ReactNode
  mode: 'sales' | 'marketing' | 'ai'
  onModeChange: (mode: 'sales' | 'marketing' | 'ai') => void
  activeNav: string
  onNavChange: (key: string) => void
  loading?: boolean
}

const sectionTitles: Record<string, string> = {
  sales: 'Sales Pipeline',
  marketing: 'Marketing Hub',
  ai: 'AI Tools',
}

export default function CopilotLayout({ children, mode, onModeChange, activeNav, onNavChange, loading }: CopilotLayoutProps) {
  const navItems = mode === 'sales' ? salesNav : mode === 'marketing' ? marketingNav : aiNav

  return (
    <div className={styles.root}>
      <header className={styles.appBar}>
        <SmartToyIcon sx={{ color: '#00c853', mr: 1.5, fontSize: 22 }} />
        <span className={styles.branding}>eTech Sales & Marketing Co-Pilot</span>
        <div className={styles.modeToggle}>
          <button
            className={`${styles.modeBtn} ${mode === 'sales' ? styles.modeBtnActive : ''}`}
            onClick={() => onModeChange('sales')}
          >
            Sales Mode
          </button>
          <button
            className={`${styles.modeBtn} ${mode === 'marketing' ? styles.modeBtnActive : ''}`}
            onClick={() => onModeChange('marketing')}
          >
            Marketing Mode
          </button>
          <button
            className={`${styles.modeBtn} ${mode === 'ai' ? styles.modeBtnActive : ''}`}
            onClick={() => onModeChange('ai')}
          >
            AI Mode
          </button>
        </div>
      </header>

      {loading && <div className={styles.loadingBar} />}

      <div className={styles.body}>
        <nav className={styles.sidebar}>
          <div className={styles.navSection}>
            <div className={styles.navSectionTitle}>
              {sectionTitles[mode]}
            </div>
            {navItems.map(item => (
              <button
                key={item.key}
                className={`${styles.navItem} ${activeNav === item.key ? styles.navItemActive : ''}`}
                onClick={() => onNavChange(item.key)}
              >
                <span className={styles.navIcon}>{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>

          <div className={styles.navSection}>
            <button
              className={`${styles.navItem} ${activeNav === 'api-explorer' ? styles.navItemActive : ''}`}
              onClick={() => onNavChange('api-explorer')}
            >
              <span className={styles.navIcon}><HelpOutlineIcon /></span>
              API Explorer
            </button>
          </div>

          <div className={styles.footer}>
            eTech S.C. — AI recommends, humans decide
          </div>
        </nav>

        <main className={styles.content}>
          {children}
        </main>
      </div>
    </div>
  )
}
