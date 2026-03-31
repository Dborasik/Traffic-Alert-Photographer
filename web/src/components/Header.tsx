import { IncidentSummary } from '../types'

interface Props {
  incidents: IncidentSummary[]
  lastRefresh: Date | null
}

export default function Header({ incidents, lastRefresh }: Props) {
  const totalSnaps   = incidents.reduce((s, i) => s + (i.snapshot_count || 0), 0)
  const totalVisible = incidents.reduce((s, i) => s + (i.visible_count  || 0), 0)

  const refreshLabel = lastRefresh
    ? lastRefresh.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : '—'

  return (
    <header>
      <div className="brand">
        <div className="brand-logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
        </div>
        <div>
          <div className="brand-name">TAP</div>
          <div className="brand-sub">Traffic Alert Photographer</div>
        </div>
      </div>

      <div className="live-dot" />
      <div className="hspacer" />

      <div className="last-refresh">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="23 4 23 10 17 10"/>
          <polyline points="1 20 1 14 7 14"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
        <span>{refreshLabel}</span>
      </div>

      <div className="stat-group">
        <div className="stat-pill s-incidents">
          <span className="s-label">Incidents</span>
          <span className="s-val">{incidents.length || '—'}</span>
        </div>
        <div className="stat-pill s-snaps">
          <span className="s-label">Snapshots</span>
          <span className="s-val">{lastRefresh ? totalSnaps : '—'}</span>
        </div>
        <div className="stat-pill s-confirmed">
          <span className="s-label">AI Confirmed</span>
          <span className="s-val">{lastRefresh ? totalVisible : '—'}</span>
        </div>
      </div>
    </header>
  )
}
