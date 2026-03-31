import { IncidentDetail } from '../types'
import CameraCard from './CameraCard'

interface Props {
  detail: IncidentDetail | null
  onImageClick: (src: string) => void
}

const TYPE_LABELS: Record<string, string> = {
  accidentsAndIncidents: 'Accident',
  roadwork:              'Roadwork',
  closures:              'Closure',
  specialEvents:         'Special Event',
  generalInfo:           'Info',
  winterDrivingIndex:    'Winter',
  transitMode:           'Transit',
}

export default function DetailPanel({ detail: d, onImageClick }: Props) {
  if (!d) {
    return (
      <div id="detail-panel">
        <div className="empty-state">
          <div className="empty-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
          </div>
          <p>Select an incident to view details</p>
        </div>
      </div>
    )
  }

  const confirmedCount = (d.cameras || []).filter(c => c.ai_visible === 1).length
  const uncertainCount = (d.cameras || []).filter(c => c.ai_visible === null).length
  const typeLabel = TYPE_LABELS[d.event_type] ?? (d.event_type || 'Unknown')

  return (
    <div id="detail-panel">
      <div className="detail-hero">
        <div className="hero-badges">
          <span className={`badge badge-type-${d.event_type || 'unknown'}`}>{typeLabel}</span>
          {d.severity && d.severity !== 'None' && d.severity !== 'Unknown' && (
            <span className={`badge badge-sev-${d.severity}`}>{d.severity}</span>
          )}
        </div>
        <h2>{d.roadway || d.id}</h2>
        <div className="hero-sub">
          <span>{d.id}</span>
          {d.direction && <><span className="sep">·</span><span>{d.direction}</span></>}
        </div>
      </div>

      <div className="stats-strip">
        <div className="stat-box">
          <div className="sb-label">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            First Seen
          </div>
          <div className="sb-val" style={{ fontSize: 13 }}>
            {d.first_seen ? new Date(d.first_seen).toLocaleString() : '—'}
          </div>
        </div>
        <div className="stat-box">
          <div className="sb-label">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            Last Updated
          </div>
          <div className="sb-val" style={{ fontSize: 13 }}>{d.last_updated || '—'}</div>
        </div>
        <div className="stat-box">
          <div className="sb-label">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
            </svg>
            Coordinates
          </div>
          <div className="sb-val mono">{d.lat?.toFixed(5)}, {d.lon?.toFixed(5)}</div>
        </div>
        <div className="stat-box">
          <div className="sb-label">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
            Cameras
          </div>
          <div className="sb-val">{d.cameras?.length || 0} checked</div>
        </div>
        <div className="stat-box">
          <div className="sb-label">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            AI Verdict
          </div>
          <div className={`sb-val${confirmedCount > 0 ? ' green' : ''}`}>
            {confirmedCount} confirmed{uncertainCount > 0 ? `, ${uncertainCount} uncertain` : ''}
          </div>
        </div>
      </div>

      <div className="detail-body">
        {d.description && <div className="desc-block">{d.description}</div>}

        {d.cameras?.length ? (
          <>
            <div className="section-hd">
              <span className="section-hd-title">Camera Views</span>
              <span className="section-hd-count">{d.cameras.length}</span>
              <span className="section-hd-line" />
            </div>
            <div className="cameras-grid">
              {d.cameras.map(c => (
                <CameraCard
                  key={c.camera_id}
                  camera={c}
                  incidentId={d.id}
                  onImageClick={onImageClick}
                />
              ))}
            </div>
          </>
        ) : (
          <div className="no-cameras">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
            No active cameras found within the configured search radius for this incident.
          </div>
        )}
      </div>
    </div>
  )
}
