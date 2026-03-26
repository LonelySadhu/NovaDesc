import { Link } from 'react-router-dom'
import { Card } from '@shared/ui/Card'
import { PriorityBadge, StatusBadge } from '@shared/ui/Badge'
import { mockWorkOrders, mockEquipmentNames, mockAssigneeNames } from '@shared/lib/mock-data'

export const WorkOrdersTable = () => (
  <Card className="flex flex-col">
    <div className="flex items-center justify-between px-5 py-4 border-b border-border-subtle">
      <h2 className="font-semibold text-sm text-text-primary">Active Work Orders</h2>
      <Link to="/work-orders" className="text-xs text-primary hover:underline">View all</Link>
    </div>

    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-border-subtle">
            {['ID', 'Title', 'Equipment', 'Priority', 'Assignee', 'Status'].map(col => (
              <th key={col} className="px-5 py-2.5 text-left text-[11px] font-medium text-text-secondary uppercase tracking-wider">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border-subtle">
          {mockWorkOrders.map(wo => (
            <tr key={wo.id} className="hover:bg-white/[0.02] transition-colors">
              <td className="px-5 py-3 text-xs font-mono text-text-muted whitespace-nowrap">
                {wo.id.toUpperCase()}
              </td>
              <td className="px-5 py-3 text-sm text-text-primary max-w-[200px] truncate">
                {wo.title}
              </td>
              <td className="px-5 py-3 text-xs text-text-secondary whitespace-nowrap">
                {mockEquipmentNames[wo.equipment_id] ?? '—'}
              </td>
              <td className="px-5 py-3">
                <PriorityBadge priority={wo.priority} />
              </td>
              <td className="px-5 py-3 text-xs text-text-secondary whitespace-nowrap">
                {wo.assigned_to ? mockAssigneeNames[wo.assigned_to] ?? '—' : '—'}
              </td>
              <td className="px-5 py-3">
                <StatusBadge status={wo.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </Card>
)
