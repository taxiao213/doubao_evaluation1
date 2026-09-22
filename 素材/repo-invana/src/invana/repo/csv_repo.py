import csv

from ..exceptions import RepoError
from ..models import Order
from ..utils.validators import require_non_empty
from .base import OrderRepository


class CsvOrderRepository(OrderRepository):
    """从订单明细 CSV 读取：order_id,customer_code,sku,qty,unit_price,tax_rate"""

    def __init__(self, path):
        self._path = path
        self._cache = None

    def _load(self):
        if self._cache is not None:
            return self._cache
        grouped = {}
        try:
            with open(self._path, newline="", encoding="utf-8") as f:
                for i, row in enumerate(csv.DictReader(f), start=2):
                    oid = require_non_empty(row["order_id"], f"第{i}行 order_id")
                    order = grouped.get(oid)
                    if order is None:
                        order = grouped[oid] = Order(
                            order_id=oid, customer_code=row["customer_code"]
                        )
                    order.add_line(row["sku"], row["qty"], row["unit_price"], row.get("tax_rate") or "0")
        except OSError as e:
            raise RepoError(f"读取订单文件失败: {e}") from e
        self._cache = list(grouped.values())
        return self._cache

    def all_orders(self):
        return self._load()

    def find(self, order_id):
        return next((o for o in self.all_orders() if o.order_id == order_id), None)
