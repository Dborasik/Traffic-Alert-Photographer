import { Camera } from '../types'

interface Props {
  camera: Camera
  incidentId: string
  onImageClick: (src: string) => void
}

export default function CameraCard({ camera: c, incidentId, onImageClick }: Props) {
  const snapSrc = c.snapshot_path
    ? `/incidents/${encodeURIComponent(incidentId)}/${c.snapshot_path}`
    : null

  const verdictCls   = c.ai_visible === 1 ? 'yes' : c.ai_visible === null ? 'uncertain' : 'no'
  const verdictLabel = c.ai_visible === 1 ? '✓ Confirmed' : c.ai_visible === null ? '? Uncertain' : '✗ Not Visible'

  return (
    <div className={`camera-card verdict-${verdictCls}`}>
      <div
        className="cam-img-wrap"
        onClick={snapSrc ? () => onImageClick(snapSrc) : undefined}
      >
        {snapSrc ? (
          <img src={snapSrc} alt={c.camera_name || ''} loading="lazy" />
        ) : (
          <div className="no-snap">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
            <span>No snapshot</span>
          </div>
        )}
        <div className={`verdict-badge ${verdictCls}`}>{verdictLabel}</div>
        {c.distance_km != null && (
          <div className="dist-badge">{c.distance_km.toFixed(3)} km</div>
        )}
      </div>

      <div className="cam-info">
        <div className="cam-header">
          <div className="cam-name">{c.camera_name || c.camera_id}</div>
          <div className="cam-id">{c.camera_id}</div>
        </div>

        <div className="cam-chips">
          {c.ai_confidence && (
            <span className={`chip chip-conf-${c.ai_confidence}`}>
              {c.ai_confidence} confidence
            </span>
          )}
          {c.ai_image_quality && (
            <span className={`chip chip-quality-${c.ai_image_quality}`}>
              img: {c.ai_image_quality}
            </span>
          )}
        </div>

        {c.ai_evidence && c.ai_evidence.length > 0 && (
          <div className="cam-evidence">
            {c.ai_evidence.map((e, idx) => (
              <span key={idx} className="ev-tag">{e}</span>
            ))}
          </div>
        )}

        {c.ai_summary && (
          <div className="cam-ai-summary">{c.ai_summary}</div>
        )}
      </div>
    </div>
  )
}
