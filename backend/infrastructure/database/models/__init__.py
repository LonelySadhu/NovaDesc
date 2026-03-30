# Импортируем все модели, чтобы Alembic видел их через Base.metadata
from .ai_assistant import AIQueryModel
from .department import DepartmentModel
from .equipment import EquipmentModel, EquipmentSystemModel
from .knowledge_base import DocumentChunkModel, KnowledgeDocumentModel
from .maintenance import MaintenanceScheduleModel
from .spare_parts import PurchaseRequestModel, SparePartModel, SparePartMovementModel
from .users import UserModel
from .work_orders import WorkOrderLogModel, WorkOrderModel, WorkOrderPhotoModel

__all__ = [
    "DepartmentModel",
    "UserModel",
    "EquipmentSystemModel",
    "EquipmentModel",
    "SparePartModel",
    "SparePartMovementModel",
    "PurchaseRequestModel",
    "WorkOrderModel",
    "WorkOrderLogModel",
    "WorkOrderPhotoModel",
    "MaintenanceScheduleModel",
    "KnowledgeDocumentModel",
    "DocumentChunkModel",
    "AIQueryModel",
]
