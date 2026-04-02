import type { WorkOrderStatus, WorkOrderPriority, WorkOrderType } from '@shared/types'

export interface WorkOrderLog {
  id: string
  work_order_id: string
  author_id: string
  message: string
  hours_spent: number
  created_at: string
}

export interface WorkOrderPhoto {
  id: string
  work_order_id: string
  uploaded_by: string
  file_path: string
  original_filename: string
  file_size: number
  caption?: string
  url?: string
  uploaded_at: string
}

export interface WorkOrder {
  id: string
  title: string
  description: string
  equipment_id: string
  created_by: string
  assigned_to?: string
  order_type: WorkOrderType
  priority: WorkOrderPriority
  status: WorkOrderStatus
  due_date?: string
  completed_at?: string
  on_hold_reason?: string
  cancellation_reason?: string
  logs: WorkOrderLog[]
  photos: WorkOrderPhoto[]
  total_hours: number
  created_at: string
  updated_at: string
}

export interface CreateWorkOrderDto {
  title: string
  description: string
  equipment_id: string
  order_type: WorkOrderType
  priority: WorkOrderPriority
  assigned_to?: string
  due_date?: string
}
