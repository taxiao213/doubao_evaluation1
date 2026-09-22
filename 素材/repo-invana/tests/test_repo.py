from invana.repo import CsvOrderRepository, InMemoryOrderRepository


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
