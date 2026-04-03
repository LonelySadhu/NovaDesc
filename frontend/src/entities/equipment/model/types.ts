import type { EquipmentStatus } from '@shared/types'

export interface MaintenanceInterval {
  value: number
  unit: 'hours' | 'days' | 'months' | 'cycles'
}

export interface Department {
  id: string
  name: string
  description: string | null
  head_id: string | null
  parent_id: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EquipmentSystem {
  id: string
  name: string
  department_id: string
  description: string | null
  system_type: string | null
  stakeholder_id: string | null
  status: 'active' | 'decommissioned'
  created_at: string
  updated_at: string
}

export interface Equipment {
  id: string
  name: string
  serial_number: string
  manufacturer: string
  model: string
  location: string
  system_id: string
  status: EquipmentStatus
  maintenance_interval?: MaintenanceInterval
  installed_at?: string
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}
