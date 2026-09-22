from abc import ABC, abstractmethod


class OrderRepository(ABC):
    @abstractmethod
    def all_orders(self): ...

    @abstractmethod
    def find(self, order_id): ...

    def by_customer(self, customer_code):
        return [o for o in self.all_orders() if o.customer_code == customer_code]
