import { IncidentSummary } from '../types'
import IncidentItem from './IncidentItem'

interface Props {
  incidents: IncidentSummary[]
  activeId: string | null
  onSelect: (id: string) => void
}

export default function IncidentList({ incidents, activeId, onSelect }: Props) {
  if (!incidents.length) {
    return (
      <div id="list-panel">
        <div className="no-results">No incidents match the current filter.</div>
      </div>
    )
  }

  return (
    <div id="list-panel">
      {incidents.map(i => (
        <IncidentItem
          key={i.id}
          incident={i}
          active={i.id === activeId}
          onClick={() => onSelect(i.id)}
        />
      ))}
    </div>
  )
}
