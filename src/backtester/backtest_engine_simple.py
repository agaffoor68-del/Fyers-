class BacktestEngine:
    def __init__(self, strategy, initial_capital=100000):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position_qty = 0
        self.trades = []

    def run(self, candles, symbol):
        print("Starting Backtest...")
        for i in range(len(candles)):
            current_candle = candles[i]
            historical_data = candles[:i + 1]
            close_price = current_candle[4]

            signal = self.strategy.on_candle(current_candle, historical_data)

            if signal == "BUY" and self.capital > 0:
                self.position_qty = self.capital / close_price
                self.capital = 0
                self.trades.append(f"BUY at {close_price:.2f}")
            elif signal == "SELL" and self.position_qty > 0:
                self.capital = self.position_qty * close_price
                self.position_qty = 0
                self.trades.append(f"SELL at {close_price:.2f}")

        final_value = self.capital if self.capital > 0 else self.position_qty * candles[-1][4]
        profit = final_value - self.initial_capital
        pnl_percent = (profit / self.initial_capital) * 100
        return final_value, profit, pnl_percent, self.trades
