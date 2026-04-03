import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi, type CreateUserDto } from '@entities/user/api/users.api'

const ROLES = [
  { value: 'engineer',   label: 'Engineer' },
  { value: 'technician', label: 'Technician' },
  { value: 'dispatcher', label: 'Dispatcher' },
  { value: 'manager',    label: 'Manager' },
  { value: 'admin',      label: 'Admin' },
]

interface Props {
  onClose: () => void
}

export const CreateUserModal = ({ onClose }: Props) => {
  const queryClient = useQueryClient()
  const [form, setForm] = useState<CreateUserDto>({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'technician',
  })
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => usersApi.create(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      onClose()
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail ?? 'Failed to create user')
    },
  })

  const set = (field: keyof CreateUserDto, value: string) =>
    setForm((f) => ({ ...f, [field]: value }))

  const valid = form.username && form.email && form.full_name && form.password

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div className="bg-bg-card border border-border-subtle rounded-card w-full max-w-md shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border-subtle">
          <h2 className="text-base font-semibold text-text-primary">New User</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-secondary transition-colors">
            <IconX />
          </button>
        </div>

        {/* Form */}
        <div className="px-5 py-4 flex flex-col gap-4">
          <Field label="Full Name">
            <input
              value={form.full_name}
              onChange={(e) => set('full_name', e.target.value)}
              placeholder="John Smith"
              className={inputCls}
            />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Username">
              <input
                value={form.username}
                onChange={(e) => set('username', e.target.value.toLowerCase().replace(/\s/g, ''))}
                placeholder="jsmith"
                className={inputCls}
              />
            </Field>
            <Field label="Role">
              <select
                value={form.role}
                onChange={(e) => set('role', e.target.value)}
                className={inputCls}
              >
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </Field>
          </div>

          <Field label="Email">
            <input
              type="email"
              value={form.email}
              onChange={(e) => set('email', e.target.value)}
              placeholder="jsmith@company.com"
              className={inputCls}
            />
          </Field>

          <Field label="Password">
            <input
              type="password"
              value={form.password}
              onChange={(e) => set('password', e.target.value)}
              placeholder="••••••••"
              className={inputCls}
            />
          </Field>

          {error && (
            <div className="text-xs text-danger bg-danger/10 border border-danger/20 rounded-lg px-3 py-2">
              {error}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 px-5 py-4 border-t border-border-subtle">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary border border-border-subtle rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => mutation.mutate()}
            disabled={!valid || mutation.isPending}
            className="px-4 py-2 text-sm font-medium bg-primary hover:bg-primary/90 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            {mutation.isPending ? 'Creating…' : 'Create User'}
          </button>
        </div>
      </div>
    </div>
  )
}

const inputCls = 'w-full bg-bg-base border border-border-subtle rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-primary/60 transition-colors'

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-text-secondary">{label}</label>
      {children}
    </div>
  )
}

function IconX() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M3 3l10 10M13 3L3 13"/>
    </svg>
  )
}
