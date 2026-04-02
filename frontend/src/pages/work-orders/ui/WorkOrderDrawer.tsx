import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { cn } from '@shared/lib/cn'
import { PriorityBadge, StatusBadge } from '@shared/ui/Badge'
import { workOrderApi } from '@entities/work-order/api/work-order.api'
import type { WorkOrder, WorkOrderPhoto } from '@entities/work-order/model/types'

interface Props {
  order: WorkOrder
  onClose: () => void
  equipmentName?: string
  onOrderUpdate: (order: WorkOrder) => void
}

export function WorkOrderDrawer({ order, onClose, equipmentName, onOrderUpdate }: Props) {
  const [tab, setTab] = useState<'logs' | 'photos'>('logs')
  const qc = useQueryClient()

  const refetch = () => qc.invalidateQueries({ queryKey: ['work-orders'] })

  const holdMutation = useMutation({
    mutationFn: () => {
      const reason = prompt('Hold reason:')
      if (!reason) return Promise.reject()
      return workOrderApi.putOnHold(order.id, reason)
    },
    onSuccess: (updated) => { onOrderUpdate(updated); refetch() },
  })

  const completeMutation = useMutation({
    mutationFn: () => workOrderApi.complete(order.id),
    onSuccess: (updated) => { onOrderUpdate(updated); refetch() },
  })

  const cancelMutation = useMutation({
    mutationFn: () => {
      const reason = prompt('Cancellation reason:')
      if (!reason) return Promise.reject()
      return workOrderApi.cancel(order.id, reason)
    },
    onSuccess: (updated) => { onOrderUpdate(updated); refetch() },
  })

  const shortId = `WO-${order.id.slice(0, 4).toUpperCase()}`

  return (
    <div className="w-[560px] flex-shrink-0 bg-bg-card border-l border-border-subtle flex flex-col h-full">
      {/* Header */}
      <div className="px-5 pt-4 pb-3 border-b border-border-subtle flex-shrink-0">
        <div className="flex items-center justify-between mb-2">
          <button onClick={onClose} className="flex items-center gap-1.5 text-text-secondary hover:text-text-primary transition-colors text-xs">
            <IconArrowLeft />
            <span className="font-mono">{shortId}</span>
          </button>
          <button className="text-text-muted hover:text-text-secondary transition-colors"><IconDots /></button>
        </div>
        <h2 className="text-lg font-semibold text-text-primary leading-snug mb-2">{order.title}</h2>
        <div className="flex items-center gap-2">
          <StatusBadge status={order.status} />
          <PriorityBadge priority={order.priority} />
        </div>
      </div>

      {/* Action buttons */}
      {order.status !== 'completed' && order.status !== 'cancelled' && (
        <div className="px-5 py-3 border-b border-border-subtle flex gap-2 flex-shrink-0">
          {(order.status === 'in_progress' || order.status === 'on_hold') && (
            <ActionButton
              label="Put on Hold"
              color="warning"
              onClick={() => holdMutation.mutate()}
              disabled={holdMutation.isPending || order.status === 'on_hold'}
            />
          )}
          {order.status !== 'on_hold' && (
            <ActionButton
              label="Complete"
              color="success"
              onClick={() => completeMutation.mutate()}
              disabled={completeMutation.isPending}
            />
          )}
          <ActionButton
            label="Cancel"
            color="danger"
            onClick={() => cancelMutation.mutate()}
            disabled={cancelMutation.isPending}
          />
        </div>
      )}

      {/* Info grid */}
      <div className="px-5 py-4 border-b border-border-subtle grid grid-cols-2 gap-x-6 gap-y-3 flex-shrink-0">
        <InfoItem label="Equipment" value={equipmentName ?? order.equipment_id.slice(0, 8) + '…'} />
        <InfoItem label="Type" value={order.order_type} capitalize />
        <InfoItem label="Assigned to" value={order.assigned_to ? order.assigned_to.slice(0, 8) + '…' : 'Unassigned'} muted={!order.assigned_to} />
        <InfoItem label="Created by" value={order.created_by.slice(0, 8) + '…'} />
        <InfoItem label="Due date" value={order.due_date ? fmtDate(order.due_date) : '—'} danger={!!order.due_date && new Date(order.due_date) < new Date() && order.status !== 'completed'} />
        <InfoItem label="Completed at" value={order.completed_at ? fmtDate(order.completed_at) : '—'} />
      </div>

      {/* Description */}
      {order.description && (
        <div className="px-5 py-3 border-b border-border-subtle flex-shrink-0">
          <p className="text-[11px] text-text-muted uppercase tracking-wider mb-1.5">Description</p>
          <p className="text-sm text-text-secondary leading-relaxed">{order.description}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="px-5 border-b border-border-subtle flex gap-5 flex-shrink-0">
        <TabButton active={tab === 'logs'} onClick={() => setTab('logs')}>Activity Log</TabButton>
        <TabButton active={tab === 'photos'} onClick={() => setTab('photos')}>
          Photos
          {order.photos.length > 0 && (
            <span className="ml-1.5 px-1.5 py-0.5 bg-primary/20 text-primary text-[10px] font-semibold rounded-pill">
              {order.photos.length}
            </span>
          )}
        </TabButton>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto">
        {tab === 'logs' ? (
          <LogsTab orderId={order.id} />
        ) : (
          <PhotosTab orderId={order.id} photos={order.photos} onUpload={() => qc.invalidateQueries({ queryKey: ['work-order', order.id] })} />
        )}
      </div>
    </div>
  )
}

// ── Logs tab ──────────────────────────────────────────────────────────────────

function LogsTab({ orderId }: { orderId: string }) {
  const [message, setMessage] = useState('')
  const [hours, setHours] = useState('')
  const qc = useQueryClient()

  const { data: logs = [], isLoading } = useQuery({
    queryKey: ['work-order-logs', orderId],
    queryFn: () => workOrderApi.listLogs(orderId),
  })

  const addLog = useMutation({
    mutationFn: () => workOrderApi.addLog(orderId, message, parseFloat(hours) || 0),
    onSuccess: () => {
      setMessage(''); setHours('')
      qc.invalidateQueries({ queryKey: ['work-order-logs', orderId] })
    },
  })

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {isLoading && <div className="text-text-muted text-sm">Loading…</div>}
        {!isLoading && logs.length === 0 && (
          <p className="text-text-muted text-sm text-center py-8">No log entries yet</p>
        )}
        {logs.map((log) => (
          <div key={log.id} className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-primary/20 text-primary text-[10px] font-bold flex items-center justify-center flex-shrink-0">
              {log.author_id.slice(0, 2).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-xs font-medium text-text-primary">{log.author_id.slice(0, 8)}…</span>
                  <p className="text-xs text-text-secondary mt-0.5">{log.message}</p>
                  <p className="text-[11px] text-text-muted mt-0.5">{timeAgo(log.created_at)}</p>
                </div>
                {log.hours_spent > 0 && (
                  <span className="flex-shrink-0 px-2 py-0.5 bg-primary/15 text-primary text-[10px] font-semibold rounded-pill">
                    {log.hours_spent}h
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add log */}
      <div className="px-5 py-4 border-t border-border-subtle flex-shrink-0">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Add a log entry…"
          rows={2}
          className="w-full bg-bg-base border border-border-subtle rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted resize-none focus:outline-none focus:border-primary/50"
        />
        <div className="flex items-center gap-2 mt-2">
          <input
            type="number"
            value={hours}
            onChange={(e) => setHours(e.target.value)}
            placeholder="Hours spent"
            min="0"
            step="0.5"
            className="w-32 bg-bg-base border border-border-subtle rounded-lg px-3 py-1.5 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-primary/50"
          />
          <button
            onClick={() => addLog.mutate()}
            disabled={!message.trim() || addLog.isPending}
            className="ml-auto px-4 py-1.5 bg-primary hover:bg-primary/90 disabled:opacity-40 text-white text-xs font-medium rounded-lg transition-colors"
          >
            {addLog.isPending ? 'Saving…' : 'Add Entry'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Photos tab ────────────────────────────────────────────────────────────────

function PhotosTab({ orderId, photos, onUpload }: { orderId: string; photos: WorkOrderPhoto[]; onUpload: () => void }) {
  const fileRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    setUploading(true)
    try {
      for (const file of Array.from(files)) {
        await workOrderApi.uploadPhoto(orderId, file)
      }
      onUpload()
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="px-5 py-4">
      {photos.length > 0 && (
        <div className="grid grid-cols-3 gap-2 mb-4">
          {photos.map((photo) => (
            <PhotoThumb key={photo.id} photo={photo} />
          ))}
        </div>
      )}

      {/* Upload zone */}
      <div
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files) }}
        className={cn(
          'border border-dashed border-border-subtle rounded-xl flex flex-col items-center justify-center py-8 gap-2 cursor-pointer transition-colors',
          uploading ? 'opacity-50 pointer-events-none' : 'hover:border-primary/40 hover:bg-primary/5',
        )}
      >
        <IconUpload />
        <p className="text-sm text-text-secondary font-medium">
          {uploading ? 'Uploading…' : 'Drop photos here or click to upload'}
        </p>
        <p className="text-xs text-text-muted">JPEG, PNG, WebP up to 20 MB</p>
      </div>
      <input
        ref={fileRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        multiple
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  )
}

function PhotoThumb({ photo }: { photo: WorkOrderPhoto }) {
  const src = photo.url ?? `data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg'/>`
  return (
    <div className="relative group rounded-lg overflow-hidden aspect-square bg-bg-base">
      <img src={src} alt={photo.original_filename} className="w-full h-full object-cover" />
      {photo.caption && (
        <div className="absolute bottom-0 left-0 right-0 bg-black/60 px-2 py-1 text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity truncate">
          {photo.caption}
        </div>
      )}
      <a
        href={photo.url}
        target="_blank"
        rel="noreferrer"
        onClick={(e) => e.stopPropagation()}
        className="absolute top-1.5 right-1.5 w-6 h-6 bg-black/50 rounded flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-white hover:bg-black/70"
      >
        <IconDownload />
      </a>
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────

function ActionButton({ label, color, onClick, disabled }: {
  label: string; color: 'warning' | 'success' | 'danger'; onClick: () => void; disabled?: boolean
}) {
  const cls = {
    warning: 'border-warning/40 text-warning hover:bg-warning/10',
    success: 'border-success/40 text-success hover:bg-success/10 bg-success/10',
    danger:  'border-danger/40 text-danger hover:bg-danger/10',
  }[color]
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn('flex-1 py-1.5 border rounded-lg text-xs font-medium transition-colors disabled:opacity-40', cls)}
    >
      {label}
    </button>
  )
}

function InfoItem({ label, value, capitalize, muted, danger }: {
  label: string; value: string; capitalize?: boolean; muted?: boolean; danger?: boolean
}) {
  return (
    <div>
      <p className="text-[11px] text-text-muted uppercase tracking-wider mb-0.5">{label}</p>
      <p className={cn('text-sm font-medium', danger ? 'text-danger' : muted ? 'text-text-muted' : 'text-text-primary', capitalize && 'capitalize')}>
        {value}
      </p>
    </div>
  )
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'py-3 text-sm font-medium transition-colors border-b-2 -mb-px flex items-center',
        active ? 'border-primary text-primary' : 'border-transparent text-text-secondary hover:text-text-primary',
      )}
    >
      {children}
    </button>
  )
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function timeAgo(iso: string) {
  const sec = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (sec < 60) return 'just now'
  if (sec < 3600) return `${Math.floor(sec / 60)}m ago`
  if (sec < 86400) return `${Math.floor(sec / 3600)}h ago`
  return `${Math.floor(sec / 86400)}d ago`
}

// ── Icons ─────────────────────────────────────────────────────────────────────
function IconArrowLeft() {
  return <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M10 3L5 8l5 5"/></svg>
}
function IconDots() {
  return <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><circle cx="8" cy="3" r="1.2"/><circle cx="8" cy="8" r="1.2"/><circle cx="8" cy="13" r="1.2"/></svg>
}
function IconUpload() {
  return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-primary"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
}
function IconDownload() {
  return <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M8 3v8M4 7l4 4 4-4M2 13h12"/></svg>
}
