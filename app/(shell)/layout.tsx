import type { ReactNode } from "react"
import Link from "next/link"
import { Home, ClipboardList, Wrench, FileText, Cpu, Bot } from "lucide-react"
import { AIPanel } from "@/components/ai/ai-panel"

export default function ShellLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r bg-background lg:flex lg:flex-col">
        <div className="p-4 text-lg font-semibold">NovaDesc</div>
        <nav className="grid gap-1 p-2">
          <NavItem href="/dashboard" label="Дэшборд" icon={<Home className="h-4 w-4" />} />
          <NavItem href="/tasks" label="Задачи" icon={<ClipboardList className="h-4 w-4" />} />
          <NavItem href="/requests" label="Заявки" icon={<Wrench className="h-4 w-4" />} />
          <NavItem href="/equipment" label="Оборудование" icon={<Cpu className="h-4 w-4" />} />
          <NavItem href="/documents" label="Документы" icon={<FileText className="h-4 w-4" />} />
        </nav>
        <div className="mt-auto p-2"><AIPanel /></div>
      </aside>

      <main className="lg:pl-64 pb-16 md:pb-0">{children}</main>

      <nav className="fixed inset-x-0 bottom-0 z-40 border-t bg-background/95 backdrop-blur lg:hidden">
        <ul className="grid grid-cols-5 text-xs">
          <TabLink href="/dashboard" label="Главная" icon={<Home />} />
          <TabLink href="/tasks" label="Задачи" icon={<ClipboardList />} />
          <TabLink href="/requests" label="Заявки" icon={<Wrench />} />
          <TabLink href="/equipment" label="Оборуд." icon={<Cpu />} />
          <TabLink href="/documents" label="Док-и" icon={<FileText />} />
        </ul>
      </nav>

      <Link href="/ai" className="fixed bottom-20 right-4 z-40 lg:hidden inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-primary-foreground shadow-md">
        <Bot className="h-4 w-4" /> AI
      </Link>
    </div>
  )
}

function NavItem({ href, label, icon }: { href: string; label: string; icon: React.ReactNode }) {
  return (
    <Link href={href} className="flex items-center gap-2 rounded-lg px-3 py-2 hover:bg-muted">
      {icon} <span>{label}</span>
    </Link>
  )
}

function TabLink({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <li>
      <Link href={href} className="flex flex-col items-center justify-center gap-1 py-2">
        <span className="h-5 w-5">{icon}</span>
        <span>{label}</span>
      </Link>
    </li>
  )
}
