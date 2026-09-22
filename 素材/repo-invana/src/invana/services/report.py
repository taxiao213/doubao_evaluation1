"""对账报表：财务对账依赖本模块输出，金额必须符合 docs/spec.md。"""
from decimal import Decimal

from ..utils.formatters import table
from .pricing import order_total


class ReportService:
    def __init__(self, repo):
        self._repo = repo

    def summary_rows(self, orders=None):
        orders = orders if orders is not None else self._repo.all_orders()
        rows = []
        for o in sorted(orders, key=lambda x: x.order_id):
            total = order_total(o)
            rows.append((o.order_id, o.customer_code, str(len(o.lines)), f"{total:.2f}"))
        return rows

    def grand_total(self, orders=None) -> Decimal:
        orders = orders if orders is not None else self._repo.all_orders()
        return sum((order_total(o) for o in orders), Decimal("0"))

    def render_text(self, orders=None) -> str:
        rows = self.summary_rows(orders)
        return table(rows, ["order_id", "customer", "lines", "total"])
