class StockService:
    """简单库存水位检查。"""

    LOW_WATER_MARK = 100

    def __init__(self, balances):
        self._balances = dict(balances)

    def is_low(self, sku: str) -> bool:
        return self._balances.get(sku, 0) < self.LOW_WATER_MARK

    def low_skus(self):
        return sorted(s for s, q in self._balances.items() if q < self.LOW_WATER_MARK)
