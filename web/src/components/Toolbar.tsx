import { FilterState } from '../types'

interface Props {
  filters: FilterState
  onFiltersChange: (f: FilterState) => void
  filteredCount: number
  totalCount: number
}

export default function Toolbar({ filters, onFiltersChange, filteredCount, totalCount }: Props) {
  const set = (patch: Partial<FilterState>) => onFiltersChange({ ...filters, ...patch })

  const countLabel = filteredCount < totalCount
    ? `${filteredCount} of ${totalCount}`
    : `${filteredCount} incidents`

  return (
    <div className="toolbar">
      <div className="search-wrap">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          type="text"
          placeholder="Search roadway, description…"
          value={filters.search}
          onChange={e => set({ search: e.target.value })}
        />
      </div>

      <select value={filters.type} onChange={e => set({ type: e.target.value })}>
        <option value="">All types</option>
        <option value="accidentsAndIncidents">Accidents &amp; Incidents</option>
        <option value="closures">Closures</option>
        <option value="winterDrivingIndex">Winter Driving</option>
        <option value="roadwork">Roadwork</option>
        <option value="specialEvents">Special Events</option>
        <option value="generalInfo">General Info</option>
      </select>

      <select value={filters.severity} onChange={e => set({ severity: e.target.value })}>
        <option value="">All severities</option>
        <option value="Major">Major</option>
        <option value="Moderate">Moderate</option>
        <option value="Minor">Minor</option>
        <option value="None">None</option>
      </select>

      <label className="toggle-pill">
        <input
          type="checkbox"
          checked={filters.visibleOnly}
          onChange={e => set({ visibleOnly: e.target.checked })}
        />
        <span className="toggle-dot" />
        AI confirmed only
      </label>

      <div className="list-count">{countLabel}</div>
    </div>
  )
}
