from .base import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    def __init__(self, orders=None):
        self._orders = list(orders or [])

    def all_orders(self):
        return list(self._orders)

    def find(self, order_id):
        return next((o for o in self._orders if o.order_id == order_id), None)

    def add(self, order):
        self._orders.append(order)
