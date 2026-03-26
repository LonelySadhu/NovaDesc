import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { lazy, Suspense } from 'react'

const DashboardPage = lazy(() => import('@pages/dashboard'))
const EquipmentPage = lazy(() => import('@pages/equipment'))
const WorkOrdersPage = lazy(() => import('@pages/work-orders'))
const MaintenancePage = lazy(() => import('@pages/maintenance'))
const AIAssistantPage = lazy(() => import('@pages/ai-assistant'))
const SettingsPage = lazy(() => import('@pages/settings'))

const router = createBrowserRouter([
  {
    path: '/',
    element: <Suspense fallback={<div>Loading...</div>}><DashboardPage /></Suspense>,
  },
  {
    path: '/equipment',
    element: <Suspense fallback={<div>Loading...</div>}><EquipmentPage /></Suspense>,
  },
  {
    path: '/work-orders',
    element: <Suspense fallback={<div>Loading...</div>}><WorkOrdersPage /></Suspense>,
  },
  {
    path: '/maintenance',
    element: <Suspense fallback={<div>Loading...</div>}><MaintenancePage /></Suspense>,
  },
  {
    path: '/ai',
    element: <Suspense fallback={<div>Loading...</div>}><AIAssistantPage /></Suspense>,
  },
  {
    path: '/settings',
    element: <Suspense fallback={<div>Loading...</div>}><SettingsPage /></Suspense>,
  },
])

export const AppRouter = () => <RouterProvider router={router} />
