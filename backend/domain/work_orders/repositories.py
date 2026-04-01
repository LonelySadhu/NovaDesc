from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import WorkOrder, WorkOrderPhoto
from .value_objects import WorkOrderPriority, WorkOrderStatus


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
    async def save(self, work_order: WorkOrder) -> None: ...

    @abstractmethod
    async def delete(self, work_order_id: UUID) -> None: ...

    @abstractmethod
    async def save_log(self, log: WorkOrderLog) -> None: ...

    @abstractmethod
    async def list_logs(self, work_order_id: UUID) -> List[WorkOrderLog]: ...

    @abstractmethod
    async def save_photo(self, photo: WorkOrderPhoto) -> None: ...

    @abstractmethod
    async def list_photos(self, work_order_id: UUID) -> List[WorkOrderPhoto]: ...
