import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { lazy, Suspense } from 'react'

const DashboardPage     = lazy(() => import('@pages/dashboard'))
const EquipmentPage     = lazy(() => import('@pages/equipment'))
const WorkOrdersPage    = lazy(() => import('@pages/work-orders'))
const MaintenancePage   = lazy(() => import('@pages/maintenance'))
const AIAssistantPage   = lazy(() => import('@pages/ai-assistant'))
const SettingsPage      = lazy(() => import('@pages/settings'))
const KnowledgeBasePage = lazy(() => import('@pages/knowledge-base'))

const Loader = () => (
  <div className="flex h-screen items-center justify-center bg-bg-base">
    <div className="w-6 h-6 rounded-full border-2 border-primary border-t-transparent animate-spin" />
  </div>
)

const wrap = (Component: React.LazyExoticComponent<() => JSX.Element>) => (
  <Suspense fallback={<Loader />}><Component /></Suspense>
)

const router = createBrowserRouter([
  { path: '/',           element: wrap(DashboardPage) },
  { path: '/equipment',  element: wrap(EquipmentPage) },
  { path: '/work-orders',element: wrap(WorkOrdersPage) },
  { path: '/maintenance',element: wrap(MaintenancePage) },
  { path: '/ai',         element: wrap(AIAssistantPage) },
  { path: '/settings',   element: wrap(SettingsPage) },
  { path: '/knowledge',  element: wrap(KnowledgeBasePage) },
])

export const AppRouter = () => <RouterProvider router={router} />
