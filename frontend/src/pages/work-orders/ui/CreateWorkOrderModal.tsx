import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { cn } from '@shared/lib/cn'
import { workOrderApi } from '@entities/work-order/api/work-order.api'
import { equipmentApi } from '@entities/equipment/api/equipment.api'
import type { WorkOrderType, WorkOrderPriority } from '@shared/types'
import type { CreateWorkOrderDto } from '@entities/work-order/model/types'

interface Props {
  onClose: () => void
}

const TYPES: { value: WorkOrderType; label: string }[] = [
  { value: 'preventive', label: 'Preventive' },
  { value: 'corrective', label: 'Corrective' },
  { value: 'inspection', label: 'Inspection' },
  { value: 'emergency',  label: 'Emergency' },
]

const PRIORITIES: { value: WorkOrderPriority; label: string; color: string }[] = [
  { value: 'low',      label: 'Low',      color: 'text-text-secondary data-[active=true]:bg-text-muted/20 data-[active=true]:text-text-primary data-[active=true]:border-text-muted/40' },
  { value: 'medium',   label: 'Medium',   color: 'text-text-secondary data-[active=true]:bg-primary/20 data-[active=true]:text-primary data-[active=true]:border-primary/40' },
  { value: 'high',     label: 'High',     color: 'text-text-secondary data-[active=true]:bg-orange/20 data-[active=true]:text-orange data-[active=true]:border-orange/40' },
  { value: 'critical', label: 'Critical', color: 'text-text-secondary data-[active=true]:bg-danger/20 data-[active=true]:text-danger data-[active=true]:border-danger/40' },
]

export function CreateWorkOrderModal({ onClose }: Props) {
  const qc = useQueryClient()

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [equipmentId, setEquipmentId] = useState('')
  const [orderType, setOrderType] = useState<WorkOrderType>('corrective')
  const [priority, setPriority] = useState<WorkOrderPriority>('medium')
  const [assignedTo, setAssignedTo] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const { data: equipment = [] } = useQuery({
    queryKey: ['equipment-list'],
    queryFn: () => equipmentApi.list({ limit: 200 }),
  })

  const createMutation = useMutation({
    mutationFn: (dto: CreateWorkOrderDto) => workOrderApi.create(dto),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['work-orders'] })
      onClose()
    },
  })

  const handleSubmit = () => {
    setSubmitted(true)
    if (!title.trim() || !equipmentId) return
    createMutation.mutate({
      title: title.trim(),
      description: description.trim(),
      equipment_id: equipmentId,
      order_type: orderType,
      priority,
      assigned_to: assignedTo || undefined,
      due_date: dueDate || undefined,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-bg-card rounded-2xl border border-border-subtle w-[520px] max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-border-subtle">
          <h2 className="text-base font-semibold text-text-primary">New Work Order</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-secondary transition-colors">
            <IconClose />
          </button>
        </div>

        {/* Form */}
        <div className="px-6 py-5 space-y-4">
          {/* Title */}
          <Field label="Title" required error={submitted && !title.trim() ? 'Required field' : undefined}>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter work order title"
              className={cn(inputCls, submitted && !title.trim() && 'border-danger/50 focus:border-danger')}
            />
          </Field>

          {/* Description */}
          <Field label="Description">
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the work to be done…"
              rows={3}
              className={cn(inputCls, 'resize-none')}
            />
          </Field>

          {/* Equipment */}
          <Field label="Equipment" required error={submitted && !equipmentId ? 'Required field' : undefined}>
            <select
              value={equipmentId}
              onChange={(e) => setEquipmentId(e.target.value)}
              className={cn(inputCls, submitted && !equipmentId && 'border-danger/50', 'appearance-none')}
            >
              <option value="">Select equipment</option>
              {equipment.map((eq) => (
                <option key={eq.id} value={eq.id}>{eq.name}</option>
              ))}
            </select>
          </Field>

          {/* Type */}
          <Field label="Type" required>
            <div className="grid grid-cols-2 gap-2">
              {TYPES.map(({ value, label }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setOrderType(value)}
                  className={cn(
                    'py-2 rounded-lg text-sm border transition-colors',
                    orderType === value
                      ? 'bg-primary/15 border-primary/40 text-primary font-medium'
                      : 'border-border-subtle text-text-secondary hover:bg-white/5',
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
          </Field>

          {/* Priority */}
          <Field label="Priority">
            <div className="grid grid-cols-4 gap-1.5">
              {PRIORITIES.map(({ value, label, color }) => (
                <button
                  key={value}
                  type="button"
                  data-active={priority === value}
                  onClick={() => setPriority(value)}
                  className={cn(
                    'py-1.5 rounded-lg text-xs border border-border-subtle transition-colors capitalize',
                    color,
                    priority !== value && 'hover:bg-white/5',
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
          </Field>

          {/* Assign to */}
          <Field label="Assign to">
            <input
              type="text"
              value={assignedTo}
              onChange={(e) => setAssignedTo(e.target.value)}
              placeholder="User ID (optional)"
              className={inputCls}
            />
          </Field>

          {/* Due date */}
          <Field label="Due Date">
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className={inputCls}
            />
          </Field>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border-subtle flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 border border-border-subtle rounded-lg text-sm text-text-secondary hover:bg-white/5 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={createMutation.isPending}
            className="flex-1 py-2.5 bg-primary hover:bg-primary/90 disabled:opacity-50 rounded-lg text-sm text-white font-medium transition-colors"
          >
            {createMutation.isPending ? 'Creating…' : 'Create Work Order'}
          </button>
        </div>
      </div>
    </div>
  )
}

function Field({ label, required, error, children }: {
  label: string; required?: boolean; error?: string; children: React.ReactNode
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-text-secondary mb-1.5">
        {label}{required && <span className="text-danger ml-0.5">*</span>}
      </label>
      {children}
      {error && <p className="text-danger text-xs mt-1">{error}</p>}
    </div>
  )
}

const inputCls = 'w-full bg-bg-base border border-border-subtle rounded-lg px-3 py-2.5 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-primary/50 transition-colors'

function IconClose() {
  return <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 3l10 10M13 3L3 13"/></svg>
}
