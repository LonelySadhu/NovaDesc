import { Link } from 'react-router-dom'
import { Card } from '@shared/ui/Card'
import { mockMaintenance } from '@shared/lib/mock-data'
import { cn } from '@shared/lib/cn'

export const MaintenanceTimeline = () => (
  <Card className="flex flex-col">
    <div className="flex items-center justify-between px-5 py-4 border-b border-border-subtle">
      <h2 className="font-semibold text-sm text-text-primary">Upcoming Maintenance</h2>
      <Link to="/maintenance" className="text-xs text-primary hover:underline">View all</Link>
    </div>

    <ul className="divide-y divide-border-subtle">
      {mockMaintenance.map(item => (
        <li key={item.id} className="flex items-start gap-4 px-5 py-3.5 hover:bg-white/[0.02] transition-colors">
          {/* Date badge */}
          <div className={cn(
            'w-10 h-10 rounded-lg flex flex-col items-center justify-center flex-shrink-0 text-center',
            item.overdue
              ? 'bg-danger/20 text-danger'
              : item.urgent
                ? 'bg-warning/20 text-warning'
                : 'bg-bg-card-hover text-text-secondary',
          )}>
            <span className="text-sm font-bold leading-none">{item.day}</span>
            <span className="text-[9px] uppercase tracking-wide leading-none mt-0.5">{item.month}</span>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm text-text-primary truncate">{item.title}</span>
              {item.overdue && (
                <span className="text-[10px] font-semibold text-danger border border-danger/30 bg-danger/10 px-1.5 py-0.5 rounded-pill flex-shrink-0">
                  OVERDUE
                </span>
              )}
            </div>
            <div className="text-xs text-text-secondary mt-0.5 truncate">{item.equipment}</div>
          </div>
        </li>
      ))}
    </ul>
  </Card>
)
