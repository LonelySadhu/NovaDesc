import { AppLayout } from '@app/layouts/AppLayout'
import { KpiCards } from '@widgets/KpiCards'
import { WorkOrdersTable } from '@widgets/WorkOrdersTable'
import { EquipmentStatusWidget } from '@widgets/EquipmentStatusWidget'
import { MaintenanceTimeline } from '@widgets/MaintenanceTimeline'
import { AiAssistantPanel } from '@widgets/AiAssistantPanel'

const DashboardPage = () => (
  <AppLayout>
    <div className="flex flex-col gap-5">
      {/* Row 1 — KPIs */}
      <KpiCards />

      {/* Row 2 — Work Orders + Equipment Status */}
      <div className="grid grid-cols-[1fr_300px] gap-5">
        <WorkOrdersTable />
        <EquipmentStatusWidget />
      </div>

      {/* Row 3 — Maintenance + AI */}
      <div className="grid grid-cols-2 gap-5">
        <MaintenanceTimeline />
        <AiAssistantPanel />
      </div>
    </div>
  </AppLayout>
)

export default DashboardPage
