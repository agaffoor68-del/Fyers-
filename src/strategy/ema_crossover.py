import pandas as pd
from strategy.base import BaseStrategy


class EMACrossover(BaseStrategy):
    def __init__(self, fast_period=9, slow_period=21):
        super().__init__()
        self.fast = fast_period
        self.slow = slow_period

    def on_candle(self, candle, historical_data):
        if len(historical_data) < self.slow:
            return "HOLD"

        closes = [c[4] for c in historical_data]
        df = pd.Series(closes)

        fast_ema = df.ewm(span=self.fast, adjust=False).mean().iloc[-1]
        slow_ema = df.ewm(span=self.slow, adjust=False).mean().iloc[-1]

        if fast_ema > slow_ema and self.position <= 0:
            self.position = 1
            return "BUY"
        elif fast_ema < slow_ema and self.position >= 0:
            self.position = -1
            return "SELL"
        return "HOLD"
