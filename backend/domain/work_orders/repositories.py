from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import WorkOrder
from .value_objects import WorkOrderStatus, WorkOrderPriority


class WorkOrderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, work_order_id: UUID) -> Optional[WorkOrder]: ...

    @abstractmethod
    async def list(
        self,
        equipment_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
        status: Optional[WorkOrderStatus] = None,
        priority: Optional[WorkOrderPriority] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[WorkOrder]: ...

    @abstractmethod
    async def save(self, work_order: WorkOrder) -> WorkOrder: ...

    @abstractmethod
    async def delete(self, work_order_id: UUID) -> None: ...
