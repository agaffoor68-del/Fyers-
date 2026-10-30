import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class TradingConfig:
    """Trading configuration parameters"""
    initial_capital: float = 100000.0
    commission: float = 0.0003  # 0.03% per trade
    slippage: float = 0.0001    # 0.01% slippage
    lot_size: int = 1
    margin_requirement: float = 0.2
    risk_per_trade: float = 0.01  # 1% risk per trade
    max_positions: int = 5
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    
@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    benchmark: str = "NSE:NIFTY50-INDEX"
    use_adjusted_close: bool = True
    handle_splits: bool = True
    handle_dividends: bool = True
    fill_method: str = "close"  # open, close, high, low
    allow_short: bool = False
    warmup_period: int = 50
