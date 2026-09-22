from dataclasses import dataclass
from .enums import ItemKind


@dataclass(frozen=True)
class Item:
    sku: str
    name: str
    kind: ItemKind = ItemKind.GOOD
    unit: str = "件"
