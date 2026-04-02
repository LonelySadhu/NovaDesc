import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AppLayout } from '@app/layouts/AppLayout'
import { cn } from '@shared/lib/cn'
import { workOrderApi } from '@entities/work-order/api/work-order.api'
import { equipmentApi } from '@entities/equipment/api/equipment.api'
import type { WorkOrder } from '@entities/work-order/model/types'
import type { WorkOrderStatus, WorkOrderPriority, WorkOrderType } from '@shared/types'
import { WorkOrdersTable } from './ui/WorkOrdersTable'
import { WorkOrderDrawer } from './ui/WorkOrderDrawer'
import { CreateWorkOrderModal } from './ui/CreateWorkOrderModal'

const STATUS_OPTIONS: { value: WorkOrderStatus | ''; label: string }[] = [
  { value: '', label: 'All Status' },
  { value: 'open', label: 'Open' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
]

const PRIORITY_OPTIONS: { value: WorkOrderPriority | ''; label: string }[] = [
  { value: '', label: 'All Priority' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
]

const TYPE_OPTIONS: { value: WorkOrderType | ''; label: string }[] = [
  { value: '', label: 'All Types' },
  { value: 'preventive', label: 'Preventive' },
  { value: 'corrective', label: 'Corrective' },
  { value: 'inspection', label: 'Inspection' },
  { value: 'emergency', label: 'Emergency' },
]

const WorkOrdersPage = () => {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<WorkOrderStatus | ''>('')
  const [priority, setPriority] = useState<WorkOrderPriority | ''>('')
  const [orderType, setOrderType] = useState<WorkOrderType | ''>('')
  const [selectedOrder, setSelectedOrder] = useState<WorkOrder | null>(null)
  const [showCreate, setShowCreate] = useState(false)

  const { data: orders = [], isLoading } = useQuery({
    queryKey: ['work-orders', status, priority, orderType],
    queryFn: () => workOrderApi.list({
      status: status || undefined,
      priority: priority || undefined,
      order_type: orderType || undefined,
      limit: 100,
    }),
  })

  const { data: equipment = [] } = useQuery({
    queryKey: ['equipment-list'],
    queryFn: () => equipmentApi.list({ limit: 500 }),
  })

  const equipmentNames = Object.fromEntries(
    equipment.map((eq) => [eq.id, eq.name])
  )

  const filtered = search.trim()
    ? orders.filter((o) => o.title.toLowerCase().includes(search.toLowerCase()))
    : orders

  return (
    <AppLayout>
      <div className="flex h-full gap-0 -m-6">
        {/* Main panel */}
        <div className={cn('flex flex-col flex-1 min-w-0 p-6 overflow-y-auto', selectedOrder && 'pr-0')}>
          {/* Header */}
          <div className="flex items-center justify-between mb-5">
            <h1 className="text-xl font-semibold text-text-primary">Work Orders</h1>
            <button
              onClick={() => setShowCreate(true)}
              className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-white text-sm font-medium rounded-xl transition-colors"
            >
              <IconPlus />
              New Work Order
            </button>
          </div>

          {/* Filters */}
          <div className="bg-bg-card rounded-card border border-border-subtle px-4 py-3 flex items-center gap-3 mb-4 flex-wrap">
            <div className="flex items-center gap-2 flex-1 min-w-[200px] bg-bg-base border border-border-subtle rounded-lg px-3 py-2">
              <IconSearch />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by title…"
                className="flex-1 bg-transparent text-sm text-text-primary placeholder-text-muted focus:outline-none"
              />
            </div>
            <FilterSelect value={status} onChange={(v) => setStatus(v as WorkOrderStatus | '')} options={STATUS_OPTIONS} />
            <FilterSelect value={priority} onChange={(v) => setPriority(v as WorkOrderPriority | '')} options={PRIORITY_OPTIONS} />
            <FilterSelect value={orderType} onChange={(v) => setOrderType(v as WorkOrderType | '')} options={TYPE_OPTIONS} />
          </div>

          {/* Table */}
          <WorkOrdersTable
            orders={filtered}
            isLoading={isLoading}
            onSelect={setSelectedOrder}
            selectedId={selectedOrder?.id}
            equipmentNames={equipmentNames}
          />

          {/* Footer */}
          {!isLoading && (
            <div className="flex items-center justify-between mt-4 text-xs text-text-muted">
              <span>
                Showing <span className="text-text-secondary font-medium">{filtered.length}</span> of{' '}
                <span className="text-text-secondary font-medium">{orders.length}</span> work orders
              </span>
              <div className="flex items-center gap-2">
                <span>Per page:</span>
                <select className="bg-bg-card border border-border-subtle rounded px-2 py-1 text-text-secondary focus:outline-none">
                  <option>20</option>
                  <option>50</option>
                  <option>100</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Drawer */}
        {selectedOrder && (
          <WorkOrderDrawer
            order={selectedOrder}
            onClose={() => setSelectedOrder(null)}
            equipmentName={equipmentNames[selectedOrder.equipment_id]}
            onOrderUpdate={setSelectedOrder}
          />
        )}
      </div>

      {/* Create modal */}
      {showCreate && <CreateWorkOrderModal onClose={() => setShowCreate(false)} />}
    </AppLayout>
  )
}

export default WorkOrdersPage

// ── Helpers ───────────────────────────────────────────────────────────────────

function FilterSelect({ value, onChange, options }: {
  value: string
  onChange: (v: string) => void
  options: { value: string; label: string }[]
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-bg-base border border-border-subtle rounded-lg px-3 py-2 text-sm text-text-secondary focus:outline-none focus:border-primary/50 cursor-pointer"
    >
      {options.map(({ value: v, label }) => (
        <option key={v} value={v}>{label}</option>
      ))}
    </select>
  )
}

function IconPlus() {
  return <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8 3v10M3 8h10"/></svg>
}
function IconSearch() {
  return <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-text-muted flex-shrink-0"><circle cx="6.5" cy="6.5" r="4.5"/><path d="M10 10l3.5 3.5"/></svg>
}
