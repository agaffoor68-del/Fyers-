# Backtesting Engine Documentation

## Overview
The Backtesting Engine is a core component of the Fyers Algorithmic Trading Platform that allows you to test trading strategies on historical data.

## Architecture

### Components

1. **BaseStrategy** (`src/strategies/base_strategy.py`) - Abstract base class for all strategies
2. **Portfolio** (`src/backtester/portfolio.py`) - Manages positions, cash, and trades
3. **Backtester** (`src/backtester/engine.py`) - Main engine that runs simulations
4. **Trade** (`src/backtester/portfolio.py`) - Represents individual trades
5. **DataLoader** (`src/data/data_loader.py`) - Loads and prepares data

## Usage

### Basic Backtest

```python
from src.backtester.engine import Backtester
from src.strategies.moving_average import MovingAverageStrategy
from src.data.data_loader import DataLoader

# Load data
loader = DataLoader()
data = loader.load_historical_data("NSE:RELIANCE-EQ", "2023-01-01", "2024-12-31")

# Create strategy
strategy = MovingAverageStrategy(short_window=20, long_window=50)

# Run backtest
backtester = Backtester(data, strategy, initial_capital=1000000)
results = backtester.run()

# View results
backtester.print_results()
```

### Custom Strategy

```python
from src.strategies.base_strategy import BaseStrategy
import pandas as pd

class RSIStrategy(BaseStrategy):
    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        super().__init__("RSIStrategy")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        df['signal'] = 0
        df.loc[df['rsi'] < self.oversold, 'signal'] = 1
        df.loc[df['rsi'] > self.overbought, 'signal'] = -1
        
        return df
```

## Metrics Calculated

- **Total Return %**: Overall return on investment
- **Sharpe Ratio**: Risk-adjusted return (annualized)
- **Max Drawdown %**: Largest peak-to-trough decline
- **Win Rate %**: Percentage of winning trades
- **Profit Factor**: Gross profit / Gross loss
- **Total Trades**: Number of completed trades

## Features

- Commission and slippage modeling
- Long-only by default (can be extended for short selling)
- Automatic position sizing
- Trade history tracking
- Equity curve generation
- Performance metrics calculation

## Notes
- The engine uses close prices for signal generation and execution
- Slippage is applied to execution prices
- Commission is deducted on each trade
 - Only closed trades are included in metrics calculations
