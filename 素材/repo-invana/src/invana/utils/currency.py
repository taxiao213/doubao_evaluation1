"""货币与舍入工具：全项目唯一的金额舍入入口。"""
from decimal import Decimal, ROUND_DOWN

from ..constants import MONEY_QUANT


def round_money(value) -> Decimal:
    """将金额保留 2 位小数。

    接受 int/float/str/Decimal，内部统一转 Decimal 后舍入。
    """
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(MONEY_QUANT, rounding=ROUND_DOWN)


def apply_tax(amount: Decimal, tax_rate: Decimal) -> Decimal:
    """按税率计算含税金额（不在此处舍入，由调用方统一舍入）。"""
    return amount * (Decimal("1") + tax_rate)


def to_display(amount: Decimal, symbol: str = "¥") -> str:
    q = round_money(amount)
    return f"{symbol}{q:,.2f}"
