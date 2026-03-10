import { apiClient } from '@shared/api/client'
import type { Equipment } from '../model/types'

export const equipmentApi = {
  list: (params?: { location?: string; status?: string; limit?: number; offset?: number }) =>
    apiClient.get<Equipment[]>('/equipment', { params }).then((r) => r.data),

  getById: (id: string) =>
    apiClient.get<Equipment>(`/equipment/${id}`).then((r) => r.data),

  create: (data: Omit<Equipment, 'id' | 'status' | 'created_at' | 'updated_at'>) =>
    apiClient.post<Equipment>('/equipment', data).then((r) => r.data),

  update: (id: string, data: Partial<Equipment>) =>
    apiClient.patch<Equipment>(`/equipment/${id}`, data).then((r) => r.data),

  decommission: (id: string) =>
    apiClient.post<Equipment>(`/equipment/${id}/decommission`).then((r) => r.data),
}
