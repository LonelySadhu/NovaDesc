import { apiClient } from '@shared/api/client'
import type { Department, Equipment, EquipmentSystem } from '../model/types'

export const departmentApi = {
  list: () =>
    apiClient.get<Department[]>('/departments').then((r) => r.data),
}

export const equipmentSystemApi = {
  listByDepartment: (department_id: string) =>
    apiClient.get<EquipmentSystem[]>('/equipment-systems', { params: { department_id } }).then((r) => r.data),
}

export const equipmentApi = {
  list: (params?: { system_id?: string; location?: string; status?: string; limit?: number; offset?: number }) =>
    apiClient.get<Equipment[]>('/equipment', { params }).then((r) => r.data),

  getById: (id: string) =>
    apiClient.get<Equipment>(`/equipment/${id}`).then((r) => r.data),

  create: (data: Omit<Equipment, 'id' | 'status' | 'created_at' | 'updated_at'>) =>
    apiClient.post<Equipment>('/equipment', data).then((r) => r.data),

  update: (id: string, data: Partial<Equipment>) =>
    apiClient.patch<Equipment>(`/equipment/${id}`, data).then((r) => r.data),

  setFault: (id: string) =>
    apiClient.post<Equipment>(`/equipment/${id}/set-fault`).then((r) => r.data),

  restore: (id: string) =>
    apiClient.post<Equipment>(`/equipment/${id}/restore`).then((r) => r.data),

  decommission: (id: string) =>
    apiClient.post<Equipment>(`/equipment/${id}/decommission`).then((r) => r.data),
}
