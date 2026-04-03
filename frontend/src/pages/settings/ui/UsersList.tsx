import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '@entities/user/api/users.api'
import type { User } from '@entities/user/model/types'
import { useAuthStore } from '@shared/store/auth.store'
import { cn } from '@shared/lib/cn'

const ROLE_LABELS: Record<string, string> = {
  admin: 'Admin', manager: 'Manager', engineer: 'Engineer',
  dispatcher: 'Dispatcher', technician: 'Technician',
}

const ROLE_COLORS: Record<string, string> = {
  admin:      'bg-danger/15 text-danger border-danger/25',
  manager:    'bg-warning/15 text-warning border-warning/25',
  engineer:   'bg-primary/15 text-primary border-primary/25',
  dispatcher: 'bg-success/15 text-success border-success/25',
  technician: 'bg-text-muted/15 text-text-secondary border-text-muted/25',
}

export const UsersList = () => {
  const queryClient = useQueryClient()
  const currentUser = useAuthStore((s) => s.user)
  const [confirmId, setConfirmId] = useState<string | null>(null)

  const { data: users = [], isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: usersApi.list,
  })

  const deactivateMutation = useMutation({
    mutationFn: (id: string) => usersApi.deactivate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      setConfirmId(null)
    },
  })

  const activateMutation = useMutation({
    mutationFn: (id: string) => usersApi.activate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  })

  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-14 rounded-card bg-bg-card animate-pulse" />
        ))}
      </div>
    )
  }

  return (
    <>
      <div className="bg-bg-card border border-border-subtle rounded-card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border-subtle">
              <th className="text-left text-xs font-medium text-text-muted px-4 py-3">User</th>
              <th className="text-left text-xs font-medium text-text-muted px-4 py-3">Username</th>
              <th className="text-left text-xs font-medium text-text-muted px-4 py-3">Role</th>
              <th className="text-left text-xs font-medium text-text-muted px-4 py-3">Status</th>
              <th className="text-left text-xs font-medium text-text-muted px-4 py-3">Created</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle">
            {users.map((user) => (
              <UserRow
                key={user.id}
                user={user}
                isSelf={user.id === currentUser?.id}
                onDeactivate={() => setConfirmId(user.id)}
                onActivate={() => activateMutation.mutate(user.id)}
                activating={activateMutation.isPending}
              />
            ))}
          </tbody>
        </table>
      </div>

      {/* Deactivate confirm */}
      {confirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-bg-card border border-border-subtle rounded-card w-full max-w-sm p-6 shadow-xl">
            <h3 className="text-base font-semibold text-text-primary mb-2">Deactivate user?</h3>
            <p className="text-sm text-text-muted mb-5">
              The user will lose access to the system immediately.
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setConfirmId(null)}
                className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary border border-border-subtle rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => deactivateMutation.mutate(confirmId)}
                disabled={deactivateMutation.isPending}
                className="px-4 py-2 text-sm font-medium bg-danger hover:bg-danger/90 disabled:opacity-50 text-white rounded-lg transition-colors"
              >
                {deactivateMutation.isPending ? 'Deactivating…' : 'Deactivate'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

function UserRow({
  user, isSelf, onDeactivate, onActivate, activating,
}: {
  user: User
  isSelf: boolean
  onDeactivate: () => void
  onActivate: () => void
  activating: boolean
}) {
  const initials = user.full_name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase()

  return (
    <tr className={cn('transition-colors', !user.is_active && 'opacity-50')}>
      <td className="px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center text-primary text-[10px] font-bold flex-shrink-0">
            {initials}
          </div>
          <div>
            <div className="text-sm font-medium text-text-primary">{user.full_name}</div>
            <div className="text-xs text-text-muted">{user.email}</div>
          </div>
        </div>
      </td>
      <td className="px-4 py-3 text-sm text-text-secondary font-mono">{user.username}</td>
      <td className="px-4 py-3">
        <span className={cn('inline-flex items-center px-2 py-0.5 rounded-pill text-[10px] font-semibold tracking-wide border', ROLE_COLORS[user.role])}>
          {ROLE_LABELS[user.role] ?? user.role}
        </span>
      </td>
      <td className="px-4 py-3">
        <span className={cn(
          'inline-flex items-center gap-1.5 text-xs',
          user.is_active ? 'text-success' : 'text-text-muted',
        )}>
          <span className={cn('w-1.5 h-1.5 rounded-full', user.is_active ? 'bg-success' : 'bg-text-muted')} />
          {user.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td className="px-4 py-3 text-xs text-text-muted">
        {new Date(user.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
      </td>
      <td className="px-4 py-3">
        {!isSelf && (
          user.is_active ? (
            <button
              onClick={onDeactivate}
              className="text-xs text-text-muted hover:text-danger transition-colors"
            >
              Deactivate
            </button>
          ) : (
            <button
              onClick={onActivate}
              disabled={activating}
              className="text-xs text-text-muted hover:text-success transition-colors disabled:opacity-50"
            >
              Activate
            </button>
          )
        )}
      </td>
    </tr>
  )
}
