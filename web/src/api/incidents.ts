import { IncidentSummary, IncidentDetail } from '../types'

export async function fetchIncidents(): Promise<IncidentSummary[]> {
  const res = await fetch('/api/incidents')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function fetchIncidentDetail(id: string): Promise<IncidentDetail> {
  const res = await fetch(`/api/incidents/${encodeURIComponent(id)}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
