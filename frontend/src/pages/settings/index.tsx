import { useState } from 'react'
import { AppLayout } from '@app/layouts/AppLayout'
import { useAuthStore } from '@shared/store/auth.store'
import { UsersList } from './ui/UsersList'
import { CreateUserModal } from './ui/CreateUserModal'

type Tab = 'users'

const SettingsPage = () => {
  const [tab, setTab] = useState<Tab>('users')
  const [showCreate, setShowCreate] = useState(false)
  const user = useAuthStore((s) => s.user)

  const isAdmin = user?.role === 'admin'

  return (
    <AppLayout>
      <div className="flex flex-col gap-5">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-text-primary">Settings</h1>
          {tab === 'users' && isAdmin && (
            <button
              onClick={() => setShowCreate(true)}
              className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-white text-sm font-medium rounded-xl transition-colors"
            >
              <IconPlus />
              New User
            </button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 border-b border-border-subtle">
          <TabButton active={tab === 'users'} onClick={() => setTab('users')}>
            <IconUsers />
            Users
          </TabButton>
        </div>

        {/* Content */}
        {tab === 'users' && <UsersList />}
      </div>

      {showCreate && <CreateUserModal onClose={() => setShowCreate(false)} />}
    </AppLayout>
  )
}

export default SettingsPage

function TabButton({ active, onClick, children }: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ${
        active
          ? 'border-primary text-primary'
          : 'border-transparent text-text-secondary hover:text-text-primary'
      }`}
    >
      {children}
    </button>
  )
}

function IconPlus() {
  return <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8 3v10M3 8h10"/></svg>
}
function IconUsers() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="6" cy="5" r="2.5"/><path d="M1 14c0-3 2-5 5-5s5 2 5 5"/>
      <circle cx="12" cy="5" r="2"/><path d="M12 10c2 0 3 1.5 3 4"/>
    </svg>
  )
}
