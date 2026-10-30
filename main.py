from src.backtester.engine import Backtester
from src.strategies.moving_average import MovingAverageStrategy
from src.data.data_loader import DataLoader

def main():
    """Example usage of the backtesting engine"""
    print("Fyers Algorithmic Trading Platform - Backtest Example")
    print("-" * 50)
    
    # Load data
    data_loader = DataLoader()
    data = data_loader.load_historical_data("NSE:SBIN-EQ", "2023-01-01", "2023-12-31")
    
    # Create strategy
    strategy = MovingAverageStrategy(short_window=10, long_window=50)
    
    # Run backtest
    backtester = Backtester(data, strategy, initial_capital=100000)
    results = backtester.run()
    
    # Print results
    backtester.print_results()
    
    # Show trades
    trades_df = backtester.get_trades_report()
    if not trades_df.empty:
        print("\nTRADE HISTORY:")
        print(trades_df.to_string())
    
    return results

if __name__ == "__main__":
    main()
