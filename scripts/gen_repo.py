# -*- coding: utf-8 -*-
"""生成 M5 测评用代码仓库：invana（库存/订单分析模拟项目）
- ≥50 个文件，模块化结构
- 预埋跨文件 bug：utils/currency.py 的舍入方向错误（ROUND_DOWN），
  符合 docs/spec.md 规范应为 ROUND_HALF_UP；症状在 services/pricing.py →
  services/report.py → tests/test_report_totals.py 中暴露（跨 3 层）。
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "素材" / "repo-invana"

FILES = {}

# ---------------- 项目级 ----------------
FILES["README.md"] = """# invana

库存与订单分析模拟项目（Python 3.10+，无第三方运行时依赖）。

## 目录结构
- `src/invana/models` 数据模型
- `src/invana/repo` 数据访问（内存 / CSV）
- `src/invana/services` 业务服务（定价、订单、报表、库存）
- `src/invana/utils` 工具（货币、日期、校验、格式化）
- `src/invana/adapters` 外部数据适配（CSV / JSON / HTTP）
- `docs/` 规范与架构说明

## 快速开始
```bash
python3 -m pytest tests/ -q          # 运行测试（PYTHONPATH 已在 pyproject 配置说明）
PYTHONPATH=src python3 -m invana.cli summary tests/fixtures/orders.csv
```

## 当前任务
1. **[BUG] `tests/test_report_totals.py` 失败**：报表订单合计金额与业务方对账结果不一致。
   请根据 `docs/spec.md` 的金额舍入规范定位根因，并以最小改动修复。
   要求：不得修改任何测试文件；修复后全部测试通过。
2. **[FEATURE]**（修复后选做）：为报表服务增加按客户分组导出 CSV 的能力，入口见 `services/report.py`。
"""
FILES["pyproject.toml"] = """[project]
name = "invana"
version = "0.3.1"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
"""
FILES[".gitignore"] = "__pycache__/\n*.pyc\n.venv/\ndist/\n"
FILES["docs/spec.md"] = """# 金额计算规范

1. 所有金额运算使用 `Decimal`，禁止使用二进制浮点直接参与金额运算。
2. 金额展示与落库一律保留 **2 位小数**，舍入方向为 **四舍五入（ROUND_HALF_UP）**。
3. 折扣、税费在行级（line）计算并舍入，订单合计为各行之和，不重复舍入。
4. 币种默认 CNY；对账以行级金额为准。
"""
FILES["docs/architecture.md"] = """# 架构说明

```
adapters ──▶ repo ──▶ services ──▶ cli
                │           │
                └── models  └── utils（currency/dates/…）
```

- `services.pricing` 是金额计算的唯一入口，所有金额必须经过 `utils.currency.round_money`。
- `services.report` 汇总行级金额生成对账报表，财务对账依赖其输出。
- `utils.currency` 是全项目唯一允许处理舍入的地方。
"""

# ---------------- 包基础 ----------------
FILES["src/invana/__init__.py"] = '"""invana：库存与订单分析。"""\n\n__version__ = "0.3.1"\n'
FILES["src/invana/config.py"] = """from pathlib import Path

DEFAULT_FIXTURE_DIR = Path("tests/fixtures")
DEFAULT_CURRENCY = "CNY"
DEFAULT_TAX_RATE = "0.005"
"""
FILES["src/invana/constants.py"] = """from decimal import Decimal

TAX_RATE = Decimal("0.005")
MONEY_QUANT = Decimal("0.01")
SCALE = 2
"""
FILES["src/invana/exceptions.py"] = """class InvanaError(Exception):
    \"\"\"项目基础异常。\"\"\"


class ValidationError(InvanaError):
    pass


class RepoError(InvanaError):
    pass


class PricingError(InvanaError):
    pass
"""

# ---------------- models ----------------
FILES["src/invana/models/__init__.py"] = (
    "from .enums import OrderStatus\n"
    "from .item import Item\n"
    "from .order import Order, OrderLine\n"
    "from .customer import Customer\n\n"
    '__all__ = ["OrderStatus", "Item", "Order", "OrderLine", "Customer"]\n'
)
FILES["src/invana/models/enums.py"] = """from enum import Enum


class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class ItemKind(str, Enum):
    GOOD = "good"
    SERVICE = "service"
"""
FILES["src/invana/models/item.py"] = """from dataclasses import dataclass
from .enums import ItemKind


@dataclass(frozen=True)
class Item:
    sku: str
    name: str
    kind: ItemKind = ItemKind.GOOD
    unit: str = "件"
"""
FILES["src/invana/models/customer.py"] = """from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    code: str
    name: str
    tier: str = "normal"
"""
FILES["src/invana/models/order.py"] = """from dataclasses import dataclass, field
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
"""

# ---------------- utils ----------------
FILES["src/invana/utils/__init__.py"] = (
    "from . import currency, dates, validators, formatters, mathx, ids, text\n"
)
FILES["src/invana/utils/currency.py"] = """\"\"\"货币与舍入工具：全项目唯一的金额舍入入口。\"\"\"
from decimal import Decimal, ROUND_DOWN

from ..constants import MONEY_QUANT


def round_money(value) -> Decimal:
    \"\"\"将金额保留 2 位小数。

    接受 int/float/str/Decimal，内部统一转 Decimal 后舍入。
    \"\"\"
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(MONEY_QUANT, rounding=ROUND_DOWN)


def apply_tax(amount: Decimal, tax_rate: Decimal) -> Decimal:
    \"\"\"按税率计算含税金额（不在此处舍入，由调用方统一舍入）。\"\"\"
    return amount * (Decimal("1") + tax_rate)


def to_display(amount: Decimal, symbol: str = "¥") -> str:
    q = round_money(amount)
    return f"{symbol}{q:,.2f}"
"""
FILES["src/invana/utils/dates.py"] = """from datetime import date, datetime


def parse_date(s: str) -> date:
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {s!r}")


def month_of(d: date) -> str:
    return d.strftime("%Y-%m")


def quarter_of(d: date) -> str:
    return f"{d.year}Q{(d.month - 1) // 3 + 1}"
"""
FILES["src/invana/utils/validators.py"] = """from ..exceptions import ValidationError


def require_non_empty(value: str, field: str):
    if not value or not value.strip():
        raise ValidationError(f"{field} 不能为空")
    return value.strip()


def require_positive_int(value, field: str) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} 必须是整数")
    if n <= 0:
        raise ValidationError(f"{field} 必须为正数")
    return n


def require_decimal_string(value, field: str) -> str:
    from decimal import Decimal, InvalidOperation
    try:
        d = Decimal(str(value))
    except InvalidOperation:
        raise ValidationError(f"{field} 必须是十进制数")
    if d < 0:
        raise ValidationError(f"{field} 不能为负")
    return str(d)
"""
FILES["src/invana/utils/formatters.py"] = """def pct(value, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def thousands(n) -> str:
    return f"{n:,}"


def table(rows, headers):
    \"\"\"极简文本表格。\"\"\"
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)] if rows else [len(str(h)) for h in headers]
    head = " | ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    sep = "-+-".join("-" * w for w in widths)
    body = [" | ".join(str(c).ljust(w) for c, w in zip(r, widths)) for r in rows]
    return "\\n".join([head, sep] + body)
"""
FILES["src/invana/utils/mathx.py"] = """from decimal import Decimal


def mean(values):
    vals = list(values)
    if not vals:
        return Decimal(0)
    return sum(vals) / len(vals)


def growth(curr, prev):
    if not prev:
        return Decimal(0)
    return (Decimal(curr) - Decimal(prev)) / Decimal(prev)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))
"""
FILES["src/invana/utils/ids.py"] = """import hashlib
import re

_SLUG_RE = re.compile(r"[^a-zA-Z0-9]+")


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.strip()).strip("-").lower()


def short_hash(text: str, n: int = 8) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]
"""
FILES["src/invana/utils/text.py"] = """def truncate(text: str, width: int, suffix: str = "…") -> str:
    if len(text) <= width:
        return text
    return text[: max(0, width - len(suffix))] + suffix


def indent(block: str, spaces: int = 2) -> str:
    pad = " " * spaces
    return "\\n".join(pad + line for line in block.splitlines())
"""

# ---------------- repo ----------------
FILES["src/invana/repo/__init__.py"] = (
    "from .base import OrderRepository\n"
    "from .memory import InMemoryOrderRepository\n"
    "from .csv_repo import CsvOrderRepository\n\n"
    '__all__ = ["OrderRepository", "InMemoryOrderRepository", "CsvOrderRepository"]\n'
)
FILES["src/invana/repo/base.py"] = """from abc import ABC, abstractmethod


class OrderRepository(ABC):
    @abstractmethod
    def all_orders(self): ...

    @abstractmethod
    def find(self, order_id): ...

    def by_customer(self, customer_code):
        return [o for o in self.all_orders() if o.customer_code == customer_code]
"""
FILES["src/invana/repo/memory.py"] = """from .base import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    def __init__(self, orders=None):
        self._orders = list(orders or [])

    def all_orders(self):
        return list(self._orders)

    def find(self, order_id):
        return next((o for o in self._orders if o.order_id == order_id), None)

    def add(self, order):
        self._orders.append(order)
"""
FILES["src/invana/repo/csv_repo.py"] = """import csv

from ..exceptions import RepoError
from ..models import Order
from ..utils.validators import require_non_empty
from .base import OrderRepository


class CsvOrderRepository(OrderRepository):
    \"\"\"从订单明细 CSV 读取：order_id,customer_code,sku,qty,unit_price,tax_rate\"\"\"

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
"""
FILES["src/invana/repo/queries.py"] = """def filter_confirmed(orders):
    from ..models import OrderStatus
    return [o for o in orders if o.status == OrderStatus.CONFIRMED]


def sort_by_total(orders, totals, desc=True):
    return sorted(orders, key=lambda o: totals.get(o.order_id, 0), reverse=desc)
"""

# ---------------- adapters ----------------
FILES["src/invana/adapters/__init__.py"] = (
    "from .csv_reader import read_rows\nfrom .json_reader import read_json\n"
)
FILES["src/invana/adapters/csv_reader.py"] = """import csv


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
"""
FILES["src/invana/adapters/json_reader.py"] = """import json


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
"""
FILES["src/invana/adapters/http_client.py"] = """import urllib.request


def get_json(url: str, timeout: float = 5.0):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()
"""
FILES["src/invana/adapters/retry.py"] = """import time


def with_retries(fn, attempts: int = 3, delay: float = 0.2):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            if i < attempts - 1:
                time.sleep(delay * (i + 1))
    raise last
"""

# ---------------- services ----------------
FILES["src/invana/services/__init__.py"] = (
    "from .pricing import line_total, order_total\n"
    "from .report import ReportService\n"
    "from .stock import StockService\n"
    "from .orders import OrderService\n"
)
FILES["src/invana/services/pricing.py"] = """\"\"\"定价与金额计算：项目内金额计算唯一入口。\"\"\"
from decimal import Decimal

from ..constants import TAX_RATE
from ..exceptions import PricingError
from ..utils.currency import apply_tax, round_money
from ..utils.validators import require_positive_int


def line_total(unit_price, qty, tax_rate=None) -> Decimal:
    \"\"\"行级含税金额 = 单价 × 数量 × (1 + 税率)，行级舍入到分。\"\"\"
    n = require_positive_int(qty, "qty")
    if n > 1_000_000:
        raise PricingError("单行数量超出上限")
    rate = TAX_RATE if tax_rate is None else Decimal(str(tax_rate))
    subtotal = Decimal(str(unit_price)) * n
    return round_money(apply_tax(subtotal, rate))


def order_total(order) -> Decimal:
    \"\"\"订单合计 = 各行级金额之和（行级已舍入，合计不重复舍入）。\"\"\"
    if not order.lines:
        return Decimal("0.00")
    total = sum(
        (line_total(ln.unit_price, ln.qty, ln.tax_rate) for ln in order.lines),
        Decimal("0"),
    )
    return total
"""
FILES["src/invana/services/orders.py"] = """from ..repo.queries import filter_confirmed
from .pricing import order_total


class OrderService:
    def __init__(self, repo):
        self._repo = repo

    def confirmed(self):
        return filter_confirmed(self._repo.all_orders())

    def totals(self, orders=None):
        orders = orders if orders is not None else self._repo.all_orders()
        return {o.order_id: order_total(o) for o in orders}

    def find(self, order_id):
        return self._repo.find(order_id)
"""
FILES["src/invana/services/stock.py"] = """class StockService:
    \"\"\"简单库存水位检查。\"\"\"

    LOW_WATER_MARK = 100

    def __init__(self, balances):
        self._balances = dict(balances)

    def is_low(self, sku: str) -> bool:
        return self._balances.get(sku, 0) < self.LOW_WATER_MARK

    def low_skus(self):
        return sorted(s for s, q in self._balances.items() if q < self.LOW_WATER_MARK)
"""
FILES["src/invana/services/report.py"] = """\"\"\"对账报表：财务对账依赖本模块输出，金额必须符合 docs/spec.md。\"\"\"
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
"""
FILES["src/invana/services/notifications.py"] = """class NotificationService:
    \"\"\"通知存根：记录事件而非真实发送。\"\"\"

    def __init__(self):
        self.sent = []

    def notify(self, channel: str, message: str):
        self.sent.append((channel, message))
        return True
"""

# ---------------- cli ----------------
FILES["src/invana/cli.py"] = """import argparse
import sys

from .repo import CsvOrderRepository
from .services import OrderService, ReportService
from .utils.text import indent


def main(argv=None):
    parser = argparse.ArgumentParser(prog="invana")
    parser.add_argument("command", choices=["summary", "totals"], help="子命令")
    parser.add_argument("orders_csv", help="订单明细 CSV 路径")
    args = parser.parse_args(argv)

    repo = CsvOrderRepository(args.orders_csv)
    if args.command == "summary":
        print(ReportService(repo).render_text())
    else:
        for oid, total in sorted(OrderService(repo).totals().items()):
            print(f"{oid}\\t{total:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""

# ---------------- tests ----------------
FILES["tests/__init__.py"] = ""
FILES["tests/conftest.py"] = """import pytest

from invana.models import Order
from invana.repo import CsvOrderRepository


@pytest.fixture
def csv_repo():
    return CsvOrderRepository("tests/fixtures/orders.csv")


@pytest.fixture
def sample_order():
    return (
        Order(order_id="SO-9001", customer_code="C-100")
        .add_line("SKU-X", 2, "10.00")
        .add_line("SKU-Y", 1, "20.00")
    )
"""
FILES["tests/test_pricing.py"] = """from decimal import Decimal

from invana.services.pricing import line_total, order_total


def test_line_total_without_tax():
    assert line_total("10.00", 2, tax_rate="0") == Decimal("20.00")


def test_line_total_with_tax_rounds_to_cents():
    # 120.00 × 2 × 1.005 = 241.20，恰好两位小数
    assert line_total("120.00", 2, tax_rate="0.005") == Decimal("241.20")


def test_line_total_rejects_bad_qty():
    import pytest
    from invana.exceptions import ValidationError
    with pytest.raises(ValidationError):
        line_total("10.00", 0)


def test_order_total_is_sum_of_lines(sample_order):
    # 10.00×2×1.005=20.10（精确两位）；20.00×1×1.005=20.10；合计 40.20
    assert order_total(sample_order) == Decimal("40.20")
"""
FILES["tests/test_report_totals.py"] = """\"\"\"财务对账基准：金额来自业务方手工复核，禁止修改本文件。\"\"\"
from decimal import Decimal

import pytest

from invana.services.report import ReportService


EXPECTED_TOTALS = {
    "SO-1001": Decimal("88.55"),
    "SO-1002": Decimal("241.20"),
    "SO-1003": Decimal("146.53"),
}
EXPECTED_GRAND = Decimal("476.28")


@pytest.fixture
def report(csv_repo):
    return ReportService(csv_repo)


def test_order_totals_match_finance(report):
    rows = {r[0]: Decimal(r[3]) for r in report.summary_rows()}
    assert rows == EXPECTED_TOTALS


def test_grand_total_matches_finance(report):
    assert report.grand_total() == EXPECTED_GRAND
"""
FILES["tests/test_validators.py"] = """import pytest

from invana.exceptions import ValidationError
from invana.utils.validators import (
    require_decimal_string,
    require_non_empty,
    require_positive_int,
)


def test_require_non_empty_strips():
    assert require_non_empty("  abc ", "f") == "abc"


def test_require_non_empty_rejects_blank():
    with pytest.raises(ValidationError):
        require_non_empty("   ", "f")


def test_require_positive_int():
    assert require_positive_int("3", "q") == 3
    with pytest.raises(ValidationError):
        require_positive_int("-1", "q")


def test_require_decimal_string():
    assert require_decimal_string("12.5", "p") == "12.5"
    with pytest.raises(ValidationError):
        require_decimal_string("abc", "p")
"""
FILES["tests/test_currency.py"] = """from decimal import Decimal

from invana.utils.currency import apply_tax, round_money, to_display


def test_round_money_passthrough():
    assert round_money(Decimal("10.00")) == Decimal("10.00")


def test_round_money_no_fraction():
    assert round_money("241.20") == Decimal("241.20")


def test_apply_tax():
    assert apply_tax(Decimal("100"), Decimal("0.005")) == Decimal("100.500")


def test_display():
    assert to_display("1234.5") == "¥1,234.50"
"""
FILES["tests/test_formatters.py"] = """from invana.utils.formatters import pct, table, thousands


def test_pct():
    assert pct(0.194) == "19.4%"


def test_thousands():
    assert thousands(1234567) == "1,234,567"


def test_table_renders_headers():
    out = table([("a", "1")], ["col1", "col2"])
    assert "col1" in out and "a" in out
"""
FILES["tests/test_repo.py"] = """from invana.repo import CsvOrderRepository, InMemoryOrderRepository


def test_memory_repo_roundtrip(sample_order):
    repo = InMemoryOrderRepository([sample_order])
    assert repo.find("SO-9001") is sample_order
    assert repo.by_customer("C-100") == [sample_order]


def test_csv_repo_groups_lines_by_order(csv_repo):
    orders = {o.order_id: o for o in csv_repo.all_orders()}
    assert set(orders) == {"SO-1001", "SO-1002", "SO-1003"}
    assert len(orders["SO-1001"].lines) == 2


def test_csv_repo_find(csv_repo):
    assert csv_repo.find("SO-1002").customer_code == "南方制造"
"""
FILES["tests/test_dates.py"] = """from datetime import date

import pytest

from invana.utils.dates import month_of, parse_date, quarter_of


def test_parse_date_formats():
    assert parse_date("2024-03-05") == date(2024, 3, 5)
    assert parse_date("2024/03/05") == date(2024, 3, 5)


def test_parse_date_rejects_garbage():
    with pytest.raises(ValueError):
        parse_date("not-a-date")


def test_month_and_quarter():
    d = date(2024, 11, 2)
    assert month_of(d) == "2024-11"
    assert quarter_of(d) == "2024Q4"
"""

# ---------------- fixtures ----------------
FILES["tests/fixtures/orders.csv"] = """order_id,customer_code,sku,qty,unit_price,tax_rate
SO-1001,华东贸易,SKU-A,1,55.00,0.005
SO-1001,华东贸易,SKU-B,1,33.10,0.005
SO-1002,南方制造,SKU-C,2,120.00,0.005
SO-1003,华东贸易,SKU-D,3,48.60,0.005
"""
FILES["tests/fixtures/orders.json"] = """{
  "orders": [
    {"order_id": "SO-2001", "customer_code": "北方科技", "lines": [{"sku": "SKU-E", "qty": 4, "unit_price": "12.35", "tax_rate": "0.005"}]}
  ]
}
"""
FILES["tests/fixtures/customers.csv"] = """code,name,tier
C-100,华东贸易,gold
C-200,南方制造,normal
C-300,北方科技,normal
"""


def main():
    count = 0
    for rel, content in FILES.items():
        p = REPO / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        count += 1
    print(f"仓库生成完成：{count} 个文件 -> {REPO}")


if __name__ == "__main__":
    main()
