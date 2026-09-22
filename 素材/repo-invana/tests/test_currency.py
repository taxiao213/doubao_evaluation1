from decimal import Decimal

from invana.utils.currency import apply_tax, round_money, to_display


def test_round_money_passthrough():
    assert round_money(Decimal("10.00")) == Decimal("10.00")


def test_round_money_no_fraction():
    assert round_money("241.20") == Decimal("241.20")


def test_apply_tax():
    assert apply_tax(Decimal("100"), Decimal("0.005")) == Decimal("100.500")


def test_display():
    assert to_display("1234.5") == "¥1,234.50"
