from invana.utils.formatters import pct, table, thousands


def test_pct():
    assert pct(0.194) == "19.4%"


def test_thousands():
    assert thousands(1234567) == "1,234,567"


def test_table_renders_headers():
    out = table([("a", "1")], ["col1", "col2"])
    assert "col1" in out and "a" in out
