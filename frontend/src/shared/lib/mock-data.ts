import type { WorkOrder } from '@entities/work-order/model/types'

export const mockWorkOrders: WorkOrder[] = [
  {
    id: 'wo-2541',
    title: 'Replace cooling fans in Server Rack A-12',
    description: 'Fans overheating, need immediate replacement',
    equipment_id: 'eq-001',
    created_by: 'user-1',
    assigned_to: undefined,
    order_type: 'corrective',
    priority: 'critical',
    status: 'in_progress',
    logs: [],
    photos: [],
    total_hours: 2.5,
    created_at: '2026-03-25T08:00:00Z',
    updated_at: '2026-03-26T09:00:00Z',
  },
  {
    id: 'wo-2540',
    title: 'Inspect hydraulic pump system',
    description: 'Scheduled quarterly inspection',
    equipment_id: 'eq-002',
    created_by: 'user-1',
    assigned_to: 'user-3',
    order_type: 'inspection',
    priority: 'high',
    status: 'in_progress',
    logs: [],
    photos: [],
    total_hours: 1.0,
    created_at: '2026-03-25T10:00:00Z',
    updated_at: '2026-03-26T10:00:00Z',
  },
  {
    id: 'wo-2539',
    title: 'Update firmware on network switches',
    description: 'Update to latest stable firmware version',
    equipment_id: 'eq-003',
    created_by: 'user-2',
    assigned_to: 'user-5',
    order_type: 'preventive',
    priority: 'medium',
    status: 'open',
    logs: [],
    photos: [],
    total_hours: 0,
    created_at: '2026-03-24T14:00:00Z',
    updated_at: '2026-03-24T14:00:00Z',
  },
  {
    id: 'wo-2538',
    title: 'Calibrate temperature sensors',
    description: 'Annual calibration of all temp sensors',
    equipment_id: 'eq-004',
    created_by: 'user-1',
    assigned_to: undefined,
    order_type: 'preventive',
    priority: 'high',
    status: 'in_progress',
    logs: [],
    photos: [],
    total_hours: 3.0,
    created_at: '2026-03-23T09:00:00Z',
    updated_at: '2026-03-26T08:00:00Z',
  },
  {
    id: 'wo-2543',
    title: 'Replace backup battery array',
    description: 'UPS battery replacement per schedule',
    equipment_id: 'eq-005',
    created_by: 'user-2',
    assigned_to: 'user-4',
    order_type: 'preventive',
    priority: 'medium',
    status: 'open',
    logs: [],
    photos: [],
    total_hours: 0,
    created_at: '2026-03-26T07:00:00Z',
    updated_at: '2026-03-26T07:00:00Z',
  },
]

export const mockEquipmentNames: Record<string, string> = {
  'eq-001': 'Server Rack A-12',
  'eq-002': 'Pump Unit B-55',
  'eq-003': 'Network SW-14',
  'eq-004': 'Temp Sensor Array',
  'eq-005': 'UPS System D-07',
}

export const mockAssigneeNames: Record<string, string> = {
  'user-3': 'J. Smith',
  'user-4': 'A. Johnson',
  'user-5': 'B. Kumar',
}

export const mockEquipmentStatus = {
  active: 78,
  under_maintenance: 14,
  fault: 5,
  decommissioned: 3,
}

export const mockMaintenance = [
  {
    id: 'm-1',
    day: 28,
    month: 'Mar',
    title: 'Quarterly cooling system inspection',
    equipment: 'Server Zone A-12',
    overdue: false,
    urgent: false,
  },
  {
    id: 'm-2',
    day: 29,
    month: 'Mar',
    title: 'Monthly hydraulic pressure check',
    equipment: 'Pump Unit B-55',
    overdue: false,
    urgent: true,
  },
  {
    id: 'm-3',
    day: 24,
    month: 'Apr',
    title: 'Oil change and filter replacement',
    equipment: 'Generator G-03',
    overdue: true,
    urgent: false,
  },
  {
    id: 'm-4',
    day: 26,
    month: 'Apr',
    title: 'Semi-annual system test',
    equipment: 'Fire Suppression Sys',
    overdue: false,
    urgent: false,
  },
]

export const mockAiQueries = [
  {
    id: 'q-1',
    question: 'What are the common causes of Server Rack A-12 overheating?',
    timeAgo: '5 min ago',
  },
  {
    id: 'q-2',
    question: 'Show me maintenance history for Pump Unit B-55',
    timeAgo: '18 min ago',
  },
  {
    id: 'q-3',
    question: 'How to replace hydraulic seals on older pump models?',
    timeAgo: '1 hr ago',
  },
]

export const mockKpis = {
  totalEquipment: 248,
  activeWorkOrders: 17,
  overdueSchedules: 5,
  aiQueriesToday: 142,
}
