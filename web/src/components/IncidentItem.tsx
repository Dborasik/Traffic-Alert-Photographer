import { IncidentSummary } from '../types'

interface Props {
  incident: IncidentSummary
  active: boolean
  onClick: () => void
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

function timeAgo(iso: string): string {
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (m <  1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

export default function IncidentItem({ incident: i, active, onClick }: Props) {
  const confirmed = (i.visible_count || 0) > 0
  const typeLabel = TYPE_LABELS[i.event_type] ?? (i.event_type || 'Unknown')

  return (
    <div
      className={`incident-item${active ? ' active' : ''}`}
      data-sev={i.severity || ''}
      onClick={onClick}
    >
      <div className="item-top">
        <div className="item-badges">
          <span className={`badge badge-type-${i.event_type || 'unknown'}`}>{typeLabel}</span>
          {i.severity && i.severity !== 'None' && i.severity !== 'Unknown' && (
            <span className={`badge badge-sev-${i.severity}`}>{i.severity}</span>
          )}
        </div>
        <span className="item-time">{i.first_seen ? timeAgo(i.first_seen) : '—'}</span>
      </div>

      <div className="item-roadway">{i.roadway || i.id}</div>
      <div className="item-desc">{i.description || '—'}</div>

      <div className="item-footer">
        <span className="item-cam-stat">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
          {i.snapshot_count || 0} snapshot{i.snapshot_count !== 1 ? 's' : ''}
        </span>
        {confirmed && (
          <span className="item-cam-stat confirmed">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            {i.visible_count} confirmed
          </span>
        )}
      </div>
    </div>
  )
}
