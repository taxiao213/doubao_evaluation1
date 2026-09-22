"""财务对账基准：金额来自业务方手工复核，禁止修改本文件。"""
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
