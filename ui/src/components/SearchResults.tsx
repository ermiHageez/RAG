import { useState } from 'react'
import type { SearchResult } from '../types'
import styles from './SearchResults.module.css'

interface SearchResultsProps {
  results: SearchResult[]
  loading: boolean
  onSearch: (query: string) => void
  onAddToPipeline: (result: SearchResult) => void
  addedIds: Set<string>
}

export default function SearchResults({ results, loading, onSearch, onAddToPipeline, addedIds }: SearchResultsProps) {
  const [query, setQuery] = useState('')

  const handleSearch = () => {
    if (!query.trim()) return
    onSearch(query.trim())
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleSearch()
    }
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.searchBar}>
        <input
          className={styles.searchInput}
          placeholder="Search for companies, sectors, or opportunities..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button className={styles.searchBtn} onClick={handleSearch} disabled={loading || !query.trim()}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {loading && <div className={styles.spinner} />}

      {!loading && results.length > 0 && (
        <div className={styles.resultCount}>{results.length} results found</div>
      )}

      {!loading && results.length > 0 && (
        <div className={styles.results}>
          {results.map((result, i) => {
            const added = addedIds.has(result.name + result.link)
            return (
              <div key={i} className={styles.card}>
                <div className={styles.cardBody}>
                  <div className={styles.cardName}>{result.name}</div>
                  <div className={styles.cardMeta}>
                    <span>{result.sector}</span>
                    {result.location && <><span>·</span><span>{result.location}</span></>}
                  </div>
                  <div className={styles.cardDesc}>{result.description}</div>
                  {result.link && (
                    <a className={styles.cardLink} href={result.link} target="_blank" rel="noopener noreferrer">
                      View source →
                    </a>
                  )}
                </div>
                <div className={styles.cardActions}>
                  <button
                    className={`${styles.addBtn} ${added ? styles.addBtnAdded : ''}`}
                    onClick={() => !added && onAddToPipeline(result)}
                    disabled={added}
                  >
                    {added ? 'Added' : '+ Add to Pipeline'}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {!loading && results.length === 0 && query && (
        <div className={styles.empty}>No results found. Try a different search term.</div>
      )}

      {!loading && !query && (
        <div className={styles.empty}>
          Enter a search query above to discover leads, companies, and opportunities.
        </div>
      )}
    </div>
  )
}
