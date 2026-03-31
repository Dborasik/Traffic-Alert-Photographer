export interface IncidentSummary {
  id: string
  event_type: string
  severity: string
  description: string
  roadway: string
  lat: number
  lon: number
  first_seen: string
  last_updated: string
  camera_count: number
  snapshot_count: number
  visible_count: number
}

export interface Camera {
  camera_id: string
  camera_name: string
  distance_km: number
  snapshot_path: string | null
  ai_visible: 1 | 0 | null
  ai_summary: string | null
  ai_confidence: 'high' | 'medium' | 'low' | null
  ai_image_quality: 'good' | 'poor' | 'unusable' | null
  ai_evidence: string[]
  captured_at: string
}

export interface IncidentDetail extends IncidentSummary {
  location: string
  direction: string
  raw_json: Record<string, unknown>
  cameras: Camera[]
}

export interface FilterState {
  search: string
  type: string
  severity: string
  visibleOnly: boolean
}
