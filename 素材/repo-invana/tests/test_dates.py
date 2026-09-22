from datetime import date

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
