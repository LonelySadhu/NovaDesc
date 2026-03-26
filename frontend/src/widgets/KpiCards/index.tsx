import { Card } from '@shared/ui/Card'
import { mockKpis } from '@shared/lib/mock-data'

interface KpiCardProps {
  value: number
  label: string
  icon: React.ReactNode
  accentClass: string
  note?: string
}

const KpiCard = ({ value, label, icon, accentClass, note }: KpiCardProps) => (
  <Card className="p-5 flex flex-col gap-3">
    <div className="flex items-start justify-between">
      <div>
        <div className={`text-3xl font-bold tracking-tight ${accentClass}`}>
          {value.toLocaleString()}
        </div>
        <div className="text-xs text-text-secondary mt-0.5">{label}</div>
      </div>
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${accentClass.replace('text-', 'bg-').split(' ')[0]}/15`}>
        <span className={`w-5 h-5 ${accentClass}`}>{icon}</span>
      </div>
    </div>
    {note && (
      <div className="text-[11px] text-text-muted border-t border-border-subtle pt-2">{note}</div>
    )}
  </Card>
)

export const KpiCards = () => (
  <div className="grid grid-cols-4 gap-4">
    <KpiCard
      value={mockKpis.totalEquipment}
      label="units registered"
      accentClass="text-cyan"
      icon={<IconServer />}
      note="+3 this month"
    />
    <KpiCard
      value={mockKpis.activeWorkOrders}
      label="work orders in progress"
      accentClass="text-primary"
      icon={<IconClipboard />}
      note="3 marked critical"
    />
    <KpiCard
      value={mockKpis.overdueSchedules}
      label="schedules overdue"
      accentClass="text-warning"
      icon={<IconAlert />}
      note="Requires attention"
    />
    <KpiCard
      value={mockKpis.aiQueriesToday}
      label="AI queries today"
      accentClass="text-success"
      icon={<IconSparkles />}
      note="via local Ollama"
    />
  </div>
)

function IconServer() {
  return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="1" y="2" width="14" height="4" rx="1"/><rect x="1" y="10" width="14" height="4" rx="1"/><circle cx="12.5" cy="4" r="0.75" fill="currentColor" stroke="none"/><circle cx="12.5" cy="12" r="0.75" fill="currentColor" stroke="none"/></svg>
}
function IconClipboard() {
  return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M5 2h6a1 1 0 011 1v10a1 1 0 01-1 1H5a1 1 0 01-1-1V3a1 1 0 011-1z"/><path d="M6 2V1h4v1"/><path d="M5 6h6M5 9h4"/></svg>
}
function IconAlert() {
  return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M8 1L15 14H1L8 1z"/><path d="M8 6v4M8 11.5v.5"/></svg>
}
function IconSparkles() {
  return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M8 1l1.5 4.5L14 7l-4.5 1.5L8 13l-1.5-4.5L2 7l4.5-1.5L8 1z"/></svg>
}
