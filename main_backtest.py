#!/usr/bin/env python3
import sys
from auth.token_manager import get_fyers_client
from data.historical import fetch_candles
from strategy.ema_crossover import EMACrossover
from backtest.engine import BacktestEngine


def main():
    print("=== FYERS ALGO TRADING PLATFORM ===")

    try:
        fyers = get_fyers_client()
        print("✅ Fyers API Connected Successfully.")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        sys.exit(1)

    symbol = "NSE:SBIN-EQ"
    candles = fetch_candles(fyers, symbol=symbol, resolution="5", days=15)

    if not candles:
        print("❌ No data received. Backtest aborted.")
        sys.exit(1)

    print(f"✅ Fetched {len(candles)} candles.")

    strategy = EMACrossover(fast_period=9, slow_period=21)
    engine = BacktestEngine(strategy, initial_capital=100000)

    final_cap, profit, pnl_percent, trades = engine.run(candles, symbol)

    print("\n========== BACKTEST RESULTS ==========")
    print(f"Symbol: {symbol}")
    print(f"Initial Capital: ₹100,000.00")
    print(f"Final Capital:   ₹{final_cap:,.2f}")
    print(f"Total PnL:       ₹{profit:,.2f} ({pnl_percent:.2f}%)")
    print(f"Total Trades:    {len(trades)}")
    print("======================================")

    if len(trades) > 0:
        print("\nLast 5 Trades:")
        for t in trades[-5:]:
            print(" -", t)


if __name__ == "__main__":
    main()
