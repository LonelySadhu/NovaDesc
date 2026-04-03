import { apiClient } from '@shared/api/client'
import type { TokenPair, User } from '../model/types'

export const authApi = {
  login: (username: string, password: string) =>
    apiClient.post<TokenPair>('/auth/login', { username, password }).then((r) => r.data),

  me: () =>
    apiClient.get<User>('/auth/me').then((r) => r.data),
}
