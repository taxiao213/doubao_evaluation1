from ..repo.queries import filter_confirmed
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
