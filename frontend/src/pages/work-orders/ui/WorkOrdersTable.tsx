import { cn } from '@shared/lib/cn'
import { PriorityBadge, StatusBadge } from '@shared/ui/Badge'
import type { WorkOrder } from '@entities/work-order/model/types'
import type { WorkOrderType } from '@shared/types'

interface Props {
  orders: WorkOrder[]
  isLoading: boolean
  onSelect: (order: WorkOrder) => void
  selectedId?: string
  equipmentNames: Record<string, string>
}

export function WorkOrdersTable({ orders, isLoading, onSelect, selectedId, equipmentNames }: Props) {
  if (isLoading) {
    return (
      <div className="bg-bg-card rounded-card border border-border-subtle">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="px-5 py-4 border-b border-border-subtle last:border-0 animate-pulse">
            <div className="h-4 bg-white/5 rounded w-1/3" />
          </div>
        ))}
      </div>
    )
  }

  if (orders.length === 0) {
    return (
      <div className="bg-bg-card rounded-card border border-border-subtle flex flex-col items-center justify-center py-16 gap-3">
        <IconClipboardEmpty />
        <p className="text-text-secondary text-sm">No work orders found</p>
        <p className="text-text-muted text-xs">Adjust filters or create a new work order</p>
      </div>
    )
  }

  return (
    <div className="bg-bg-card rounded-card border border-border-subtle overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border-subtle">
              {['ID', 'Title', 'Type', 'Equipment', 'Priority', 'Assignee', 'Due Date', 'Status', ''].map((col) => (
                <th key={col} className="px-4 py-3 text-left text-[11px] font-medium text-text-secondary uppercase tracking-wider whitespace-nowrap">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle">
            {orders.map((order) => (
              <WorkOrderRow
                key={order.id}
                order={order}
                isSelected={order.id === selectedId}
                onClick={() => onSelect(order)}
                equipmentName={equipmentNames[order.equipment_id]}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function WorkOrderRow({
  order, isSelected, onClick, equipmentName,
}: {
  order: WorkOrder
  isSelected: boolean
  onClick: () => void
  equipmentName?: string
}) {
  const isOverdue = order.due_date && new Date(order.due_date) < new Date() && order.status !== 'completed' && order.status !== 'cancelled'
  const shortId = `WO-${order.id.slice(0, 4).toUpperCase()}`

  return (
    <tr
      onClick={onClick}
      className={cn(
        'cursor-pointer transition-colors',
        isSelected ? 'bg-primary/10' : 'hover:bg-white/[0.02]',
      )}
    >
      <td className="px-4 py-3 text-xs font-mono text-text-muted whitespace-nowrap">{shortId}</td>
      <td className="px-4 py-3 text-sm text-text-primary max-w-[200px]">
        <span className="truncate block">{order.title}</span>
      </td>
      <td className="px-4 py-3 whitespace-nowrap">
        <TypeChip type={order.order_type} />
      </td>
      <td className="px-4 py-3 text-xs text-text-secondary whitespace-nowrap max-w-[140px]">
        <span className="truncate block">{equipmentName ?? '—'}</span>
      </td>
      <td className="px-4 py-3">
        <PriorityBadge priority={order.priority} />
      </td>
      <td className="px-4 py-3 text-xs text-text-secondary whitespace-nowrap">
        {order.assigned_to ? <Assignee userId={order.assigned_to} /> : <span className="text-text-muted">Unassigned</span>}
      </td>
      <td className="px-4 py-3 text-xs whitespace-nowrap">
        {order.due_date ? (
          <span className={cn('flex items-center gap-1', isOverdue ? 'text-danger' : 'text-text-secondary')}>
            {isOverdue && <IconOverdue />}
            {formatDate(order.due_date)}
            {isOverdue && <span className="text-[10px]">({daysOverdue(order.due_date)}d overdue)</span>}
          </span>
        ) : (
          <span className="text-text-muted">—</span>
        )}
      </td>
      <td className="px-4 py-3">
        <StatusBadge status={order.status} />
      </td>
      <td className="px-4 py-3">
        <button
          onClick={(e) => { e.stopPropagation(); onClick() }}
          className="text-text-muted hover:text-text-secondary transition-colors p-1"
        >
          <IconDots />
        </button>
      </td>
    </tr>
  )
}

function TypeChip({ type }: { type: WorkOrderType }) {
  const config: Record<WorkOrderType, { label: string; icon: JSX.Element; color: string }> = {
    corrective:  { label: 'Corrective',  icon: <IconWrench />,   color: 'text-cyan' },
    preventive:  { label: 'Preventive',  icon: <IconShield />,   color: 'text-primary' },
    inspection:  { label: 'Inspection',  icon: <IconEye />,      color: 'text-warning' },
    emergency:   { label: 'Emergency',   icon: <IconBolt />,     color: 'text-danger' },
  }
  const { label, icon, color } = config[type]
  return (
    <span className={cn('flex items-center gap-1.5 text-xs', color)}>
      <span className="w-3.5 h-3.5">{icon}</span>
      {label}
    </span>
  )
}

function Assignee({ userId }: { userId: string }) {
  const initials = userId.slice(0, 2).toUpperCase()
  return (
    <span className="flex items-center gap-1.5">
      <span className="w-5 h-5 rounded-full bg-primary/30 text-primary text-[9px] font-bold flex items-center justify-center flex-shrink-0">
        {initials}
      </span>
      <span className="text-text-secondary">{userId.slice(0, 8)}…</span>
    </span>
  )
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function daysOverdue(iso: string) {
  return Math.floor((Date.now() - new Date(iso).getTime()) / 86400000)
}

// ── Icons ─────────────────────────────────────────────────────────────────────

function IconClipboardEmpty() {
  return (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-text-muted">
      <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
      <rect x="9" y="3" width="6" height="4" rx="1"/>
    </svg>
  )
}
function IconWrench() {
  return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M10.5 2a3.5 3.5 0 00-3.36 4.47L2 11.59 2.41 14l2.41.41 5.12-5.14A3.5 3.5 0 1010.5 2z"/></svg>
}
function IconShield() {
  return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M8 1L2 4v4c0 3.31 2.67 6.41 6 7 3.33-.59 6-3.69 6-7V4L8 1z"/></svg>
}
function IconEye() {
  return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M1 8s3-5 7-5 7 5 7 5-3 5-7 5-7-5-7-5z"/><circle cx="8" cy="8" r="2"/></svg>
}
function IconBolt() {
  return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M9 1L4 9h5l-2 6 7-9h-5l2-5z"/></svg>
}
function IconOverdue() {
  return <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="8" cy="8" r="7"/><path d="M8 5v3.5l2 2"/></svg>
}
function IconDots() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <circle cx="8" cy="3" r="1.2"/><circle cx="8" cy="8" r="1.2"/><circle cx="8" cy="13" r="1.2"/>
    </svg>
  )
}
