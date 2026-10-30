import pytest
import pandas as pd
from datetime import datetime
from src.strategies.moving_average import MovingAverageStrategy
from src.backtester.portfolio import Portfolio, Trade
from src.backtester.engine import Backtester
from src.data.data_loader import DataLoader

class TestMovingAverageStrategy:
    def test_strategy_initialization(self):
        strategy = MovingAverageStrategy(short_window=10, long_window=50)
        assert strategy.short_window == 10
        assert strategy.long_window == 50
        assert strategy.name == "MovingAverageCrossover"
    
    def test_generate_signals(self):
        data_loader = DataLoader()
        data = data_loader.generate_sample_data("TEST", "2023-01-01", "2023-03-31")
        strategy = MovingAverageStrategy(short_window=5, long_window=20)
        signals = strategy.generate_signals(data)
        assert 'signal' in signals.columns
        assert signals['signal'].isin([-1, 0, 1]).all()

class TestPortfolio:
    def test_portfolio_initialization(self):
        portfolio = Portfolio(initial_capital=100000)
        assert portfolio.cash == 100000
        assert len(portfolio.positions) == 0
        assert len(portfolio.trades) == 0
    
    def test_buy_order(self):
        portfolio = Portfolio(initial_capital=100000)
        success = portfolio.buy("TEST", 10, 100, datetime.now())
        assert success == True
        assert portfolio.cash < 100000
        assert "TEST" in portfolio.positions
    
    def test_sell_order(self):
        portfolio = Portfolio(initial_capital=100000)
        portfolio.buy("TEST", 10, 100, datetime.now())
        success = portfolio.sell("TEST", 10, 110, datetime.now())
        assert success == True
        assert len([t for t in portfolio.trades if t.status == 'CLOSED']) == 1

class TestBacktester:
    def test_backtest_run(self):
        data_loader = DataLoader()
        data = data_loader.generate_sample_data("TEST", "2023-01-01", "2023-06-30")
        strategy = MovingAverageStrategy(short_window=10, long_window=30)
        backtester = Backtester(data, strategy, initial_capital=100000)
        results = backtester.run()
        assert 'total_return_pct' in results
        assert 'sharpe_ratio' in results
        assert 'max_drawdown_pct' in results
        assert len(backtester.equity_curve) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
