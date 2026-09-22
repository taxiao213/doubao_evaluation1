from enum import Enum


class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class ItemKind(str, Enum):
    GOOD = "good"
    SERVICE = "service"
