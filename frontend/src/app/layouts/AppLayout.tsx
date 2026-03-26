import { NavLink } from 'react-router-dom'
import type { ReactNode } from 'react'
import { cn } from '@shared/lib/cn'

const navItems = [
  { to: '/',            label: 'Dashboard',           icon: <IconGrid /> },
  { to: '/equipment',   label: 'Equipment',            icon: <IconServer /> },
  { to: '/work-orders', label: 'Work Orders',          icon: <IconClipboard /> },
  { to: '/maintenance', label: 'Maintenance Schedule', icon: <IconCalendar /> },
  { to: '/ai',          label: 'AI Assistant',         icon: <IconSparkles /> },
  { to: '/knowledge',   label: 'Knowledge Base',       icon: <IconBook /> },
  { to: '/settings',    label: 'Settings',             icon: <IconSettings /> },
]

export const AppLayout = ({ children }: { children: ReactNode }) => (
  <div className="flex h-screen bg-bg-base text-text-primary font-sans overflow-hidden">
    {/* Sidebar */}
    <aside className="w-60 flex-shrink-0 bg-bg-sidebar border-r border-border-subtle flex flex-col">
      {/* Logo */}
      <div className="h-14 flex items-center gap-2.5 px-5 border-b border-border-subtle">
        <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1L13 4V10L7 13L1 10V4L7 1Z" stroke="white" strokeWidth="1.5" strokeLinejoin="round"/>
            <circle cx="7" cy="7" r="2" fill="white"/>
          </svg>
        </div>
        <span className="font-semibold text-sm tracking-wide text-text-primary">NovaDesc</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-0.5">
        {navItems.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-primary/15 text-primary font-medium'
                  : 'text-text-secondary hover:text-text-primary hover:bg-white/5',
              )
            }
          >
            <span className="w-4 h-4 flex-shrink-0">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="px-4 py-4 border-t border-border-subtle flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center text-primary text-xs font-bold flex-shrink-0">
          JD
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-text-primary truncate">John Doe</div>
          <div className="text-[11px] text-text-secondary truncate">Technician</div>
        </div>
        <button className="text-text-muted hover:text-text-secondary transition-colors" title="Logout">
          <IconLogout />
        </button>
      </div>
    </aside>

    {/* Main */}
    <main className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <header className="h-14 flex items-center justify-between px-6 border-b border-border-subtle flex-shrink-0">
        <h1 className="font-semibold text-base text-text-primary">Dashboard</h1>
        <div className="flex items-center gap-3">
          <button className="relative text-text-secondary hover:text-text-primary transition-colors">
            <IconBell />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-danger rounded-full text-[9px] font-bold flex items-center justify-center text-white">3</span>
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-primary/15 hover:bg-primary/25 border border-primary/30 text-primary text-xs font-medium rounded-lg transition-colors">
            <IconSparkles />
            Ask AI
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {children}
      </div>
    </main>
  </div>
)

// ── Inline SVG icons ──────────────────────────────────────────────────────────

function IconGrid() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="1" y="1" width="6" height="6" rx="1"/><rect x="9" y="1" width="6" height="6" rx="1"/>
      <rect x="1" y="9" width="6" height="6" rx="1"/><rect x="9" y="9" width="6" height="6" rx="1"/>
    </svg>
  )
}
function IconServer() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="1" y="2" width="14" height="4" rx="1"/>
      <rect x="1" y="10" width="14" height="4" rx="1"/>
      <circle cx="12.5" cy="4" r="0.75" fill="currentColor" stroke="none"/>
      <circle cx="12.5" cy="12" r="0.75" fill="currentColor" stroke="none"/>
    </svg>
  )
}
function IconClipboard() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M5 2h6a1 1 0 011 1v10a1 1 0 01-1 1H5a1 1 0 01-1-1V3a1 1 0 011-1z"/>
      <path d="M6 2V1h4v1"/><path d="M5 6h6M5 9h4"/>
    </svg>
  )
}
function IconCalendar() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="1" y="3" width="14" height="12" rx="1.5"/>
      <path d="M1 7h14M5 1v4M11 1v4"/>
    </svg>
  )
}
function IconSparkles() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M8 1l1.5 4.5L14 7l-4.5 1.5L8 13l-1.5-4.5L2 7l4.5-1.5L8 1z"/>
    </svg>
  )
}
function IconBook() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M2 2h5a2 2 0 012 2v10a2 2 0 00-2-2H2V2zM14 2H9a2 2 0 00-2 2v10a2 2 0 012-2h5V2z"/>
    </svg>
  )
}
function IconSettings() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="8" cy="8" r="2.5"/>
      <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.42 1.42M11.53 11.53l1.42 1.42M3.05 12.95l1.42-1.42M11.53 4.47l1.42-1.42"/>
    </svg>
  )
}
function IconBell() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M8 1a5 5 0 015 5v3l1 2H2l1-2V6a5 5 0 015-5zM6.5 13.5a1.5 1.5 0 003 0"/>
    </svg>
  )
}
function IconLogout() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M6 2H3a1 1 0 00-1 1v10a1 1 0 001 1h3M10 11l4-3-4-3M14 8H6"/>
    </svg>
  )
}
