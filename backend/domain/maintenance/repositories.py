from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .entities import MaintenanceSchedule


class MaintenanceScheduleRepository(ABC):
    @abstractmethod
    async def get_by_id(self, schedule_id: UUID) -> Optional[MaintenanceSchedule]: ...

    @abstractmethod
    async def list_by_equipment(
        self, equipment_id: UUID, active_only: bool = False
    ) -> List[MaintenanceSchedule]: ...

    @abstractmethod
    async def list_overdue(self) -> List[MaintenanceSchedule]: ...

    @abstractmethod
    async def save(self, schedule: MaintenanceSchedule) -> None: ...

    @abstractmethod
    async def delete(self, schedule_id: UUID) -> None: ...
