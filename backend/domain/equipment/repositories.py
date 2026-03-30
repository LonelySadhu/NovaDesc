from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import Equipment, EquipmentSystem
from .value_objects import EquipmentStatus


class EquipmentSystemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, system_id: UUID) -> Optional[EquipmentSystem]: ...

    @abstractmethod
    async def list_by_department(self, department_id: UUID) -> List[EquipmentSystem]: ...

    @abstractmethod
    async def save(self, system: EquipmentSystem) -> None: ...

    @abstractmethod
    async def delete(self, system_id: UUID) -> None: ...


class EquipmentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, equipment_id: UUID) -> Optional[Equipment]: ...

    @abstractmethod
    async def get_by_serial(self, serial: str) -> Optional[Equipment]: ...

    @abstractmethod
    async def list(
        self,
        system_id: Optional[UUID] = None,
        status: Optional[EquipmentStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Equipment]: ...

    @abstractmethod
    async def save(self, equipment: Equipment) -> None: ...

    @abstractmethod
    async def delete(self, equipment_id: UUID) -> None: ...
