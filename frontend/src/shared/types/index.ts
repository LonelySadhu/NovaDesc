export type UserRole = 'admin' | 'manager' | 'engineer' | 'dispatcher' | 'technician'

export type EquipmentStatus = 'active' | 'under_maintenance' | 'decommissioned' | 'fault'

export type WorkOrderStatus = 'open' | 'in_progress' | 'on_hold' | 'completed' | 'cancelled'

export type WorkOrderPriority = 'low' | 'medium' | 'high' | 'critical'

export type WorkOrderType = 'preventive' | 'corrective' | 'inspection' | 'emergency'

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}
