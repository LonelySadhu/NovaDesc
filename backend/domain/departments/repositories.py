from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import Department


class DepartmentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, department_id: UUID) -> Optional[Department]: ...

    @abstractmethod
    async def list_all(self, include_inactive: bool = False) -> List[Department]: ...

    @abstractmethod
    async def save(self, department: Department) -> None: ...

    @abstractmethod
    async def delete(self, department_id: UUID) -> None: ...
