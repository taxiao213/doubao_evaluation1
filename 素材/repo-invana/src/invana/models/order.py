from dataclasses import dataclass, field
from .enums import OrderStatus


@dataclass
class OrderLine:
    sku: str
    qty: int
    unit_price: str  # 十进制字符串，如 "55.00"
    tax_rate: str = "0.005"

    @property
    def unit_price_decimal(self):
        from decimal import Decimal
        return Decimal(self.unit_price)


@dataclass
class Order:
    order_id: str
    customer_code: str
    lines: list = field(default_factory=list)
    status: OrderStatus = OrderStatus.CONFIRMED

    def add_line(self, sku: str, qty: int, unit_price: str, tax_rate: str = "0.005"):
        self.lines.append(OrderLine(sku=sku, qty=qty, unit_price=unit_price, tax_rate=tax_rate))
        return self
