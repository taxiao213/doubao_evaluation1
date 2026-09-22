import pytest

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
