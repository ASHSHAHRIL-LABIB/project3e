class LowStockStrategy:
    def is_low(self, stock, threshold):
        raise NotImplementedError


class ThresholdLowStockStrategy(LowStockStrategy):
    def is_low(self, stock, threshold):
        return stock <= threshold
