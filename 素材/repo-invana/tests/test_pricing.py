from decimal import Decimal

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
