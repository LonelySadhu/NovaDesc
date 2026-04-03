import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { cn } from '@shared/lib/cn'
import { departmentApi, equipmentApi, equipmentSystemApi } from '@entities/equipment/api/equipment.api'
import type { Department, Equipment, EquipmentSystem } from '@entities/equipment/model/types'

interface EquipmentTreeProps {
  selectedId: string | null
  onSelect: (equipment: Equipment) => void
}

export const EquipmentTree = ({ selectedId, onSelect }: EquipmentTreeProps) => {
  const { data: departments = [], isLoading } = useQuery({
    queryKey: ['departments'],
    queryFn: () => departmentApi.list(),
  })

  if (isLoading) {
    return (
      <div className="flex flex-col gap-2 p-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-8 rounded-lg bg-bg-card animate-pulse" />
        ))}
      </div>
    )
  }

  if (departments.length === 0) {
    return (
      <div className="p-4 text-sm text-text-muted text-center">No departments found</div>
    )
  }

  return (
    <div className="flex flex-col">
      {departments.filter((d) => d.is_active).map((dept) => (
        <DepartmentNode
          key={dept.id}
          department={dept}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}

// ── Department node ────────────────────────────────────────────────────────────

function DepartmentNode({
  department,
  selectedId,
  onSelect,
}: {
  department: Department
  selectedId: string | null
  onSelect: (eq: Equipment) => void
}) {
  const [open, setOpen] = useState(false)

  const { data: systems = [], isLoading } = useQuery({
    queryKey: ['equipment-systems', department.id],
    queryFn: () => equipmentSystemApi.listByDepartment(department.id),
    enabled: open,
  })

  return (
    <div>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-white/5 transition-colors rounded-lg"
      >
        <ChevronIcon open={open} />
        <IconBuilding />
        <span className="flex-1 text-left truncate font-medium">{department.name}</span>
      </button>

      {open && (
        <div className="ml-4 border-l border-border-subtle">
          {isLoading && <Skeleton />}
          {!isLoading && systems.length === 0 && (
            <div className="px-4 py-2 text-xs text-text-muted">No systems</div>
          )}
          {systems.map((sys) => (
            <SystemNode
              key={sys.id}
              system={sys}
              selectedId={selectedId}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// ── System node ────────────────────────────────────────────────────────────────

function SystemNode({
  system,
  selectedId,
  onSelect,
}: {
  system: EquipmentSystem
  selectedId: string | null
  onSelect: (eq: Equipment) => void
}) {
  const [open, setOpen] = useState(false)

  const { data: items = [], isLoading } = useQuery({
    queryKey: ['equipment', 'system', system.id],
    queryFn: () => equipmentApi.list({ system_id: system.id, limit: 500 }),
    enabled: open,
  })

  return (
    <div>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-white/5 transition-colors rounded-lg"
      >
        <ChevronIcon open={open} />
        <IconSystem />
        <span className="flex-1 text-left truncate">{system.name}</span>
        {system.system_type && (
          <span className="text-[10px] text-text-muted shrink-0">{system.system_type}</span>
        )}
      </button>

      {open && (
        <div className="ml-4 border-l border-border-subtle">
          {isLoading && <Skeleton />}
          {!isLoading && items.length === 0 && (
            <div className="px-4 py-2 text-xs text-text-muted">No equipment</div>
          )}
          {items.map((eq) => (
            <EquipmentItem
              key={eq.id}
              equipment={eq}
              selected={eq.id === selectedId}
              onClick={() => onSelect(eq)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// ── Equipment leaf ─────────────────────────────────────────────────────────────

function EquipmentItem({
  equipment,
  selected,
  onClick,
}: {
  equipment: Equipment
  selected: boolean
  onClick: () => void
}) {
  const dot = {
    active: 'bg-success',
    under_maintenance: 'bg-primary',
    fault: 'bg-danger',
    decommissioned: 'bg-text-muted',
  }[equipment.status]

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors rounded-lg',
        selected
          ? 'bg-primary/15 text-primary'
          : 'text-text-secondary hover:text-text-primary hover:bg-white/5',
      )}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', dot)} />
      <span className="flex-1 text-left truncate">{equipment.name}</span>
    </button>
  )
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      width="10" height="10" viewBox="0 0 10 10" fill="none"
      stroke="currentColor" strokeWidth="1.5"
      className={cn('flex-shrink-0 transition-transform', open && 'rotate-90')}
    >
      <path d="M3 2l4 3-4 3" />
    </svg>
  )
}

function IconBuilding() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="flex-shrink-0 text-text-muted">
      <rect x="2" y="3" width="12" height="12" rx="1" />
      <path d="M5 15V9h6v6M8 3V1M5 6h1M10 6h1M5 9h1M10 9h1" />
    </svg>
  )
}

function IconSystem() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="flex-shrink-0 text-text-muted">
      <rect x="1" y="4" width="14" height="4" rx="1" />
      <rect x="1" y="10" width="14" height="3" rx="1" />
      <circle cx="12.5" cy="6" r="0.75" fill="currentColor" stroke="none" />
      <circle cx="12.5" cy="11.5" r="0.75" fill="currentColor" stroke="none" />
    </svg>
  )
}

function Skeleton() {
  return (
    <div className="flex flex-col gap-1 px-3 py-1">
      {[1, 2].map((i) => (
        <div key={i} className="h-6 rounded bg-bg-card animate-pulse" />
      ))}
    </div>
  )
}
