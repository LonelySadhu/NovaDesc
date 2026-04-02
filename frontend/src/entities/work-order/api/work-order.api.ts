import { apiClient } from '@shared/api/client'
import type { WorkOrder, WorkOrderLog, WorkOrderPhoto, CreateWorkOrderDto } from '../model/types'
import type { WorkOrderStatus, WorkOrderPriority, WorkOrderType } from '@shared/types'

export interface ListWorkOrdersParams {
  status?: WorkOrderStatus
  priority?: WorkOrderPriority
  order_type?: WorkOrderType
  equipment_id?: string
  assigned_to?: string
  limit?: number
  offset?: number
}

export const workOrderApi = {
  list: (params?: ListWorkOrdersParams) =>
    apiClient.get<WorkOrder[]>('/work-orders/', { params }).then((r) => r.data),

  getById: (id: string) =>
    apiClient.get<WorkOrder>(`/work-orders/${id}`).then((r) => r.data),

  create: (data: CreateWorkOrderDto) =>
    apiClient.post<WorkOrder>('/work-orders/', data).then((r) => r.data),

  assign: (id: string, technician_id: string) =>
    apiClient.post<WorkOrder>(`/work-orders/${id}/assign`, { technician_id }).then((r) => r.data),

  putOnHold: (id: string, reason: string) =>
    apiClient.post<WorkOrder>(`/work-orders/${id}/hold`, { reason }).then((r) => r.data),

  complete: (id: string) =>
    apiClient.post<WorkOrder>(`/work-orders/${id}/complete`).then((r) => r.data),

  cancel: (id: string, reason: string) =>
    apiClient.post<WorkOrder>(`/work-orders/${id}/cancel`, { reason }).then((r) => r.data),

  listLogs: (id: string) =>
    apiClient.get<WorkOrderLog[]>(`/work-orders/${id}/logs`).then((r) => r.data),

  addLog: (id: string, message: string, hours_spent: number) =>
    apiClient.post<WorkOrderLog>(`/work-orders/${id}/logs`, { message, hours_spent }).then((r) => r.data),

  listPhotos: (id: string) =>
    apiClient.get<WorkOrderPhoto[]>(`/work-orders/${id}/photos`).then((r) => r.data),

  uploadPhoto: (id: string, file: File, caption?: string) => {
    const form = new FormData()
    form.append('file', file)
    if (caption) form.append('caption', caption)
    return apiClient.post<WorkOrderPhoto>(`/work-orders/${id}/photos`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },
}
