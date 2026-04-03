import { create } from 'zustand'
import { authApi } from '@entities/user/api/auth.api'
import type { User } from '@entities/user/model/types'

interface AuthState {
  user: User | null
  accessToken: string | null
  isLoading: boolean

  login: (username: string, password: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: localStorage.getItem('access_token'),
  isLoading: false,

  login: async (username, password) => {
    const tokens = await authApi.login(username, password)
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    set({ accessToken: tokens.access_token })
    const user = await authApi.me()
    set({ user })
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, accessToken: null })
    window.location.href = '/login'
  },

  loadUser: async () => {
    const token = get().accessToken
    if (!token) return
    set({ isLoading: true })
    try {
      const user = await authApi.me()
      set({ user })
    } catch {
      get().logout()
    } finally {
      set({ isLoading: false })
    }
  },
}))
