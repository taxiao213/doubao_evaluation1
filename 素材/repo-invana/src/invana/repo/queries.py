def filter_confirmed(orders):
    from ..models import OrderStatus
    return [o for o in orders if o.status == OrderStatus.CONFIRMED]


def sort_by_total(orders, totals, desc=True):
    return sorted(orders, key=lambda o: totals.get(o.order_id, 0), reverse=desc)
