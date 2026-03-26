import { cn } from '@shared/lib/cn'
import type { WorkOrderPriority, WorkOrderStatus } from '@shared/types'

const priorityConfig: Record<WorkOrderPriority, { label: string; className: string }> = {
  critical: { label: 'CRITICAL', className: 'bg-danger/20 text-danger border-danger/30' },
  high:     { label: 'HIGH',     className: 'bg-orange/20 text-orange border-orange/30' },
  medium:   { label: 'MEDIUM',   className: 'bg-primary/20 text-primary border-primary/30' },
  low:      { label: 'LOW',      className: 'bg-text-muted/20 text-text-secondary border-text-muted/30' },
}

const statusConfig: Record<WorkOrderStatus, { label: string; className: string }> = {
  in_progress: { label: 'IN PROGRESS', className: 'bg-primary/20 text-primary border-primary/30' },
  open:        { label: 'OPEN',        className: 'bg-text-muted/20 text-text-secondary border-text-muted/30' },
  on_hold:     { label: 'ON HOLD',     className: 'bg-warning/20 text-warning border-warning/30' },
  completed:   { label: 'COMPLETED',   className: 'bg-success/20 text-success border-success/30' },
  cancelled:   { label: 'CANCELLED',   className: 'bg-text-muted/20 text-text-muted border-text-muted/30' },
}

interface PriorityBadgeProps {
  priority: WorkOrderPriority
  className?: string
}

interface StatusBadgeProps {
  status: WorkOrderStatus
  className?: string
}

const basePill = 'inline-flex items-center px-2 py-0.5 rounded-pill text-[10px] font-semibold tracking-wide border'

export const PriorityBadge = ({ priority, className }: PriorityBadgeProps) => {
  const config = priorityConfig[priority]
  return <span className={cn(basePill, config.className, className)}>{config.label}</span>
}

export const StatusBadge = ({ status, className }: StatusBadgeProps) => {
  const config = statusConfig[status]
  return <span className={cn(basePill, config.className, className)}>{config.label}</span>
}
