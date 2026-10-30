from engine.backtest_engine import BacktestEngine
from strategy.ema_crossover import EMACrossover
from data.fyers_data_fetcher import fetch_candles
from executors.fyers_client import get_fyers_client

def main():
    try:
        fyers = get_fyers_client()
        candles = fetch_candles(fyers, symbol="NSE:SBIN-EQ", resolution="5", days=15)
        if not candles:
            print("No candles fetched. Exiting.")
            return
        strategy = EMACrossover(fast_period=9, slow_period=21)
        engine = BacktestEngine(strategy)
        result = engine.run(candles, "NSE:SBIN-EQ")
        print("Final Value:", result[0])
        print("Profit:", result[1])
        print("P&L %:", result[2])
        print("Trades:", result[3])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
