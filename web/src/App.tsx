import { useState, useEffect } from 'react'
import { IncidentSummary, IncidentDetail, FilterState } from './types'
import { fetchIncidents, fetchIncidentDetail } from './api/incidents'
import Header from './components/Header'
import Toolbar from './components/Toolbar'
import IncidentList from './components/IncidentList'
import DetailPanel from './components/DetailPanel'
import Lightbox from './components/Lightbox'

export default function App() {
  const [allIncidents, setAllIncidents] = useState<IncidentSummary[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [detail, setDetail] = useState<IncidentDetail | null>(null)
  const [lightboxSrc, setLightboxSrc] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    type: '',
    severity: '',
    visibleOnly: false,
  })

  async function loadIncidents() {
    try {
      const data = await fetchIncidents()
      setAllIncidents(data)
      setLastRefresh(new Date())
    } catch (e) {
      console.error('Failed to load incidents', e)
    }
  }

  useEffect(() => {
    loadIncidents()
    const interval = setInterval(loadIncidents, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (!activeId) { setDetail(null); return }
    fetchIncidentDetail(activeId).then(setDetail).catch(console.error)
  }, [activeId])

  const filtered = allIncidents.filter(i => {
    if (filters.type && i.event_type !== filters.type) return false
    if (filters.severity && i.severity !== filters.severity) return false
    if (filters.visibleOnly && !i.visible_count) return false
    if (filters.search && !`${i.roadway} ${i.description}`.toLowerCase().includes(filters.search.toLowerCase())) return false
    return true
  })

  return (
    <>
      <Header incidents={allIncidents} lastRefresh={lastRefresh} />
      <Toolbar
        filters={filters}
        onFiltersChange={setFilters}
        filteredCount={filtered.length}
        totalCount={allIncidents.length}
      />
      <div className="layout">
        <IncidentList incidents={filtered} activeId={activeId} onSelect={setActiveId} />
        <DetailPanel detail={detail} onImageClick={setLightboxSrc} />
      </div>
      <Lightbox src={lightboxSrc} onClose={() => setLightboxSrc(null)} />
      <footer>
        <span>
          Data source:{' '}
          <a href="https://www.511NY.org" target="_blank" rel="noopener">511NY</a>{' '}
          (NYSDOT) — TAP is not affiliated with or endorsed by 511NY or NYSDOT.
        </span>
        <span className="footer-disclaimer">
          Data provided "as is" with no warranty. Accuracy subject to change. Actual conditions may vary.
        </span>
      </footer>
    </>
  )
}
