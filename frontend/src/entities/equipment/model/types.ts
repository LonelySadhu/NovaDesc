import type { EquipmentStatus } from '@shared/types'

export interface MaintenanceInterval {
  value: number
  unit: 'hours' | 'days' | 'months' | 'cycles'
}

export interface Equipment {
  id: string
  name: string
  serial_number: string
  manufacturer: string
  model: string
  location: string
  status: EquipmentStatus
  maintenance_interval?: MaintenanceInterval
  installed_at?: string
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}
