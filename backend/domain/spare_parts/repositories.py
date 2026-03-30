from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import PurchaseRequest, SparePart, SparePartMovement
from .value_objects import PurchaseRequestStatus, SparePartStatus


class SparePartRepository(ABC):
    @abstractmethod
    async def get_by_id(self, spare_part_id: UUID) -> Optional[SparePart]: ...

    @abstractmethod
    async def list_by_equipment(self, equipment_id: UUID) -> List[SparePart]: ...

    @abstractmethod
    async def list_low_stock(self) -> List[SparePart]: ...

    @abstractmethod
    async def save(self, spare_part: SparePart) -> None: ...

    @abstractmethod
    async def save_movement(self, movement: SparePartMovement) -> None: ...


class PurchaseRequestRepository(ABC):
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional[PurchaseRequest]: ...

    @abstractmethod
    async def list_by_status(self, status: PurchaseRequestStatus) -> List[PurchaseRequest]: ...

    @abstractmethod
    async def list_by_spare_part(self, spare_part_id: UUID) -> List[PurchaseRequest]: ...

    @abstractmethod
    async def save(self, request: PurchaseRequest) -> None: ...
