from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import Equipment


class EquipmentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, equipment_id: UUID) -> Optional[Equipment]: ...

    @abstractmethod
    async def get_by_serial(self, serial: str) -> Optional[Equipment]: ...

    @abstractmethod
    async def list(
        self,
        location: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Equipment]: ...

    @abstractmethod
    async def save(self, equipment: Equipment) -> Equipment: ...

    @abstractmethod
    async def delete(self, equipment_id: UUID) -> None: ...
