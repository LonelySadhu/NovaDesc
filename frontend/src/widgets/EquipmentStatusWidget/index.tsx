import { Card } from '@shared/ui/Card'
import { mockEquipmentStatus } from '@shared/lib/mock-data'

// SVG donut chart — no external deps
const RADIUS = 52
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const CENTER = 68

interface Segment {
  key: keyof typeof mockEquipmentStatus
  label: string
  color: string
}

const segments: Segment[] = [
  { key: 'active',            label: 'Active',           color: '#22C55E' },
  { key: 'under_maintenance', label: 'Under Maintenance', color: '#EAB308' },
  { key: 'fault',             label: 'Fault',            color: '#EF4444' },
  { key: 'decommissioned',    label: 'Decommissioned',   color: '#4B5563' },
]

const DonutChart = () => {
  let offset = 0
  const total = Object.values(mockEquipmentStatus).reduce((a, b) => a + b, 0)

  return (
    <svg width={CENTER * 2} height={CENTER * 2} viewBox={`0 0 ${CENTER * 2} ${CENTER * 2}`}>
      {segments.map(({ key, color }) => {
        const pct = mockEquipmentStatus[key] / total
        const dash = pct * CIRCUMFERENCE
        const gap = CIRCUMFERENCE - dash
        const rotation = (offset / total) * 360 - 90
        offset += mockEquipmentStatus[key]

        return (
          <circle
            key={key}
            cx={CENTER}
            cy={CENTER}
            r={RADIUS}
            fill="none"
            stroke={color}
            strokeWidth="20"
            strokeDasharray={`${dash} ${gap}`}
            strokeDashoffset={0}
            transform={`rotate(${rotation} ${CENTER} ${CENTER})`}
            strokeLinecap="butt"
          />
        )
      })}
      {/* Center text */}
      <text x={CENTER} y={CENTER - 6} textAnchor="middle" fill="#F0F4FF" fontSize="22" fontWeight="700">
        {mockEquipmentStatus.active}%
      </text>
      <text x={CENTER} y={CENTER + 12} textAnchor="middle" fill="#9CA3AF" fontSize="10">
        Active
      </text>
    </svg>
  )
}

export const EquipmentStatusWidget = () => (
  <Card className="flex flex-col">
    <div className="px-5 py-4 border-b border-border-subtle">
      <h2 className="font-semibold text-sm text-text-primary">Equipment Status</h2>
    </div>

    <div className="flex flex-col items-center py-5 gap-5">
      <DonutChart />

      {/* Legend */}
      <div className="grid grid-cols-2 gap-x-6 gap-y-2 w-full px-5">
        {segments.map(({ key, label, color }) => (
          <div key={key} className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: color }} />
            <span className="text-xs text-text-secondary truncate">{label}</span>
            <span className="text-xs text-text-primary font-medium ml-auto">
              {mockEquipmentStatus[key]}%
            </span>
          </div>
        ))}
      </div>
    </div>

    {/* Next maintenance callout */}
    <div className="mx-4 mb-4 p-3 bg-primary/10 border border-primary/20 rounded-lg flex items-start gap-2.5">
      <span className="text-primary mt-0.5">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="1" y="3" width="14" height="12" rx="1.5"/>
          <path d="M1 7h14M5 1v4M11 1v4"/>
        </svg>
      </span>
      <div>
        <div className="text-xs font-medium text-text-primary">Next scheduled maintenance in 2 days</div>
        <div className="text-[11px] text-text-secondary mt-0.5">Cooling Unit #A-12</div>
      </div>
    </div>
  </Card>
)
