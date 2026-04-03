import type { ReactNode } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { equipmentApi } from '@entities/equipment/api/equipment.api'
import type { Equipment } from '@entities/equipment/model/types'
import { EquipmentStatusBadge } from '@shared/ui/Badge'
import { Card } from '@shared/ui/Card'

interface EquipmentDetailProps {
  equipment: Equipment
  onUpdate: (eq: Equipment) => void
}

export const EquipmentDetail = ({ equipment, onUpdate }: EquipmentDetailProps) => {
  const queryClient = useQueryClient()

  const invalidate = (updated: Equipment) => {
    queryClient.invalidateQueries({ queryKey: ['equipment', 'system', updated.system_id] })
    onUpdate(updated)
  }

  const faultMutation = useMutation({
    mutationFn: () => equipmentApi.setFault(equipment.id),
    onSuccess: invalidate,
  })

  const restoreMutation = useMutation({
    mutationFn: () => equipmentApi.restore(equipment.id),
    onSuccess: invalidate,
  })

  const canSetFault = equipment.status === 'active' || equipment.status === 'under_maintenance'
  const canRestore = equipment.status === 'fault' || equipment.status === 'under_maintenance'

  const metaTags = Object.entries(equipment.metadata).filter(([, v]) => v !== null && v !== '')

  return (
    <div className="flex flex-col gap-4 p-6 overflow-y-auto h-full">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold text-text-primary leading-snug">{equipment.name}</h2>
          <p className="text-sm text-text-muted mt-0.5">{equipment.manufacturer} · {equipment.model}</p>
        </div>
        <EquipmentStatusBadge status={equipment.status} className="mt-0.5 flex-shrink-0" />
      </div>

      {/* Main info */}
      <Card className="divide-y divide-border-subtle">
        <DetailRow label="Serial Number" value={equipment.serial_number} mono />
        <DetailRow label="Manufacturer" value={equipment.manufacturer} />
        <DetailRow label="Model" value={equipment.model} />
        <DetailRow label="Location" value={equipment.location} />
        {equipment.installed_at && (
          <DetailRow label="Installed" value={formatDate(equipment.installed_at)} />
        )}
      </Card>

      {/* Maintenance interval */}
      {equipment.maintenance_interval && (
        <section>
          <SectionLabel>Maintenance Interval</SectionLabel>
          <Card className="px-4 py-3 flex items-center gap-3">
            <IconClock />
            <span className="text-sm text-text-primary font-medium">
              Every {equipment.maintenance_interval.value}{' '}
              {equipment.maintenance_interval.unit}
            </span>
          </Card>
        </section>
      )}

      {/* Metadata tags */}
      {metaTags.length > 0 && (
        <section>
          <SectionLabel>Tags / Metadata</SectionLabel>
          <div className="flex flex-wrap gap-2">
            {metaTags.map(([key, val]) => (
              <span
                key={key}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-bg-card border border-border-subtle text-xs text-text-secondary"
              >
                <span className="text-text-muted">{key}:</span>
                <span>{String(val)}</span>
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Actions */}
      {(canSetFault || canRestore) && (
        <section>
          <SectionLabel>Actions</SectionLabel>
          <div className="flex gap-2">
            {canSetFault && (
              <ActionButton
                label="Set Fault"
                variant="danger"
                loading={faultMutation.isPending}
                onClick={() => faultMutation.mutate()}
              />
            )}
            {canRestore && (
              <ActionButton
                label="Restore"
                variant="success"
                loading={restoreMutation.isPending}
                onClick={() => restoreMutation.mutate()}
              />
            )}
          </div>
        </section>
      )}

      {/* Timestamps */}
      <div className="mt-auto pt-4 border-t border-border-subtle flex flex-col gap-1">
        <TimestampRow label="Created" value={equipment.created_at} />
        <TimestampRow label="Updated" value={equipment.updated_at} />
      </div>
    </div>
  )
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function DetailRow({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-4 px-4 py-3">
      <span className="text-xs text-text-muted flex-shrink-0">{label}</span>
      <span className={`text-sm text-text-primary text-right truncate ${mono ? 'font-mono' : ''}`}>
        {value}
      </span>
    </div>
  )
}

function TimestampRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between text-xs text-text-muted">
      <span>{label}</span>
      <span>{formatDate(value)}</span>
    </div>
  )
}

function SectionLabel({ children }: { children: ReactNode }) {
  return <div className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">{children}</div>
}

function ActionButton({
  label,
  variant,
  loading,
  onClick,
}: {
  label: string
  variant: 'danger' | 'success'
  loading: boolean
  onClick: () => void
}) {
  const cls = variant === 'danger'
    ? 'bg-danger/10 hover:bg-danger/20 text-danger border-danger/30'
    : 'bg-success/10 hover:bg-success/20 text-success border-success/30'

  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors disabled:opacity-50 ${cls}`}
    >
      {loading ? 'Loading…' : label}
    </button>
  )
}

function IconClock() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-text-muted flex-shrink-0">
      <circle cx="8" cy="8" r="6.5" />
      <path d="M8 4.5V8l2.5 2" />
    </svg>
  )
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}
