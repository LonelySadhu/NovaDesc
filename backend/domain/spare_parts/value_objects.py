from enum import Enum


class SparePartStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"       # количество ≤ min_stock_level
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"  # снят с производства


class WriteOffReason(str, Enum):
    DEFECT = "defect"             # брак
    NON_CONFORMITY = "non_conformity"  # несоответствие требованиям
    REPLACED = "replaced"         # замена после проведения работ
    EXPIRED = "expired"           # истёк срок годности
    DAMAGED = "damaged"           # повреждение при хранении/транспортировке


class PurchaseRequestStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"       # отправлена на согласование
    APPROVED = "approved"
    REJECTED = "rejected"
    ORDERED = "ordered"           # заказ размещён у поставщика
    RECEIVED = "received"         # получено на склад
    CANCELLED = "cancelled"
