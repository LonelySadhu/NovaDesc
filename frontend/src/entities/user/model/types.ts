import type { UserRole } from '@shared/types'

export interface User {
  id: string
  username: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  department_id: string | null
  created_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}
