import { apiClient } from '@shared/api/client'
import type { User } from '../model/types'

export interface CreateUserDto {
  username: string
  email: string
  full_name: string
  password: string
  role: string
  department_id?: string | null
}

export interface UpdateUserDto {
  full_name?: string
  email?: string
  role?: string
  department_id?: string | null
  password?: string
}

export const usersApi = {
  list: () =>
    apiClient.get<User[]>('/users/').then((r) => r.data),

  create: (data: CreateUserDto) =>
    apiClient.post<User>('/users/', data).then((r) => r.data),

  update: (id: string, data: UpdateUserDto) =>
    apiClient.patch<User>(`/users/${id}`, data).then((r) => r.data),

  deactivate: (id: string) =>
    apiClient.post<User>(`/users/${id}/deactivate`).then((r) => r.data),

  activate: (id: string) =>
    apiClient.post<User>(`/users/${id}/activate`).then((r) => r.data),
}
