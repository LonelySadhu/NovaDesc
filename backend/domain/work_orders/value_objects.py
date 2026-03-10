from enum import Enum


class WorkOrderStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrderPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkOrderType(str, Enum):
    PREVENTIVE = "preventive"    # плановое ТО
    CORRECTIVE = "corrective"    # аварийный ремонт
    INSPECTION = "inspection"    # осмотр/проверка
    EMERGENCY = "emergency"      # экстренное
