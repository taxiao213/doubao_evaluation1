"""定价与金额计算：项目内金额计算唯一入口。"""
from decimal import Decimal

from ..constants import TAX_RATE
from ..exceptions import PricingError
from ..utils.currency import apply_tax, round_money
from ..utils.validators import require_positive_int


def line_total(unit_price, qty, tax_rate=None) -> Decimal:
    """行级含税金额 = 单价 × 数量 × (1 + 税率)，行级舍入到分。"""
    n = require_positive_int(qty, "qty")
    if n > 1_000_000:
        raise PricingError("单行数量超出上限")
    rate = TAX_RATE if tax_rate is None else Decimal(str(tax_rate))
    subtotal = Decimal(str(unit_price)) * n
    return round_money(apply_tax(subtotal, rate))


def order_total(order) -> Decimal:
    """订单合计 = 各行级金额之和（行级已舍入，合计不重复舍入）。"""
    if not order.lines:
        return Decimal("0.00")
    total = sum(
        (line_total(ln.unit_price, ln.qty, ln.tax_rate) for ln in order.lines),
        Decimal("0"),
    )
    return total
