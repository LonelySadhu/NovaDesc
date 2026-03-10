from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ENGINEER = "engineer"
    DISPATCHER = "dispatcher"
    TECHNICIAN = "technician"
