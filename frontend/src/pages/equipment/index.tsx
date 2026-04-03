import { useState } from 'react'
import { AppLayout } from '@app/layouts/AppLayout'
import type { Equipment } from '@entities/equipment/model/types'
import { EquipmentTree } from './ui/EquipmentTree'
import { EquipmentDetail } from './ui/EquipmentDetail'

const EquipmentPage = () => {
  const [selected, setSelected] = useState<Equipment | null>(null)

  return (
    <AppLayout>
      <div className="flex h-full gap-0 -m-6">
        {/* Tree panel */}
        <div className="w-72 flex-shrink-0 border-r border-border-subtle flex flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-border-subtle flex-shrink-0">
            <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              Equipment Tree
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto py-1 px-1">
            <EquipmentTree
              selectedId={selected?.id ?? null}
              onSelect={setSelected}
            />
          </div>
        </div>

        {/* Detail panel */}
        <div className="flex-1 overflow-hidden">
          {selected ? (
            <EquipmentDetail
              key={selected.id}
              equipment={selected}
              onUpdate={setSelected}
            />
          ) : (
            <EmptyState />
          )}
        </div>
      </div>
    </AppLayout>
  )
}

export default EquipmentPage

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
      <div className="w-12 h-12 rounded-xl bg-bg-card border border-border-subtle flex items-center justify-center">
        <IconServer />
      </div>
      <div>
        <p className="text-sm font-medium text-text-secondary">Select equipment</p>
        <p className="text-xs text-text-muted mt-0.5">
          Choose a unit from the tree on the left
        </p>
      </div>
    </div>
  )
}

function IconServer() {
  return (
    <svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-text-muted">
      <rect x="1" y="2" width="14" height="4" rx="1" />
      <rect x="1" y="10" width="14" height="4" rx="1" />
      <circle cx="12.5" cy="4" r="0.75" fill="currentColor" stroke="none" />
      <circle cx="12.5" cy="12" r="0.75" fill="currentColor" stroke="none" />
    </svg>
  )
}
