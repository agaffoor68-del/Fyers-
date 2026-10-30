import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from src.utils.logger import get_logger

class Trade:
    """Represents a single trade"""
    def __init__(self, symbol: str, side: str, quantity: int, entry_price: float, 
                 entry_date: datetime, stop_loss: float = None, take_profit: float = None):
        self.symbol = symbol
        self.side = side  # 'BUY' or 'SELL'
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.exit_price = None
        self.exit_date = None
        self.pnl = 0.0
        self.pnl_pct = 0.0
        self.commission = 0.0
        self.status = 'OPEN'  # OPEN, CLOSED
    
    def close_trade(self, exit_price: float, exit_date: datetime, commission: float = 0.0):
        """Close the trade"""
        self.exit_price = exit_price
        self.exit_date = exit_date
        self.commission = commission
        self.status = 'CLOSED'
        
        if self.side == 'BUY':
            self.pnl = (self.exit_price - self.entry_price) * self.quantity - commission
            self.pnl_pct = ((self.exit_price - self.entry_price) / self.entry_price) * 100
        elif self.side == 'SELL':
            self.pnl = (self.entry_price - self.exit_price) * self.quantity - commission
            self.pnl_pct = ((self.entry_price - self.exit_price) / self.entry_price) * 100
    
    def __repr__(self):
        return f"Trade({self.symbol}, {self.side}, qty={self.quantity}, entry={self.entry_price}, status={self.status})"

class Portfolio:
    """Manages portfolio state and positions"""
    def __init__(self, initial_capital: float = 100000.0, commission: float = 0.0003):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission = commission
        self.positions = {}  # symbol -> {'quantity': int, 'avg_price': float}
        self.trades = []
        self.logger = get_logger("Portfolio")
    
    def get_position(self, symbol: str):
        """Get current position for symbol"""
        return self.positions.get(symbol, {'quantity': 0, 'avg_price': 0.0})
    
    def buy(self, symbol: str, quantity: int, price: float, date: datetime) -> bool:
        """Execute buy order"""
        cost = quantity * price * (1 + self.commission)
        if cost > self.cash:
            self.logger.warning(f"Insufficient funds to buy {quantity} {symbol} at {price}")
            return False
        
        # Update cash
        self.cash -= cost
        
        # Update position
        if symbol in self.positions and self.positions[symbol]['quantity'] > 0:
            existing_qty = self.positions[symbol]['quantity']
            existing_price = self.positions[symbol]['avg_price']
            total_qty = existing_qty + quantity
            total_cost = (existing_qty * existing_price) + (quantity * price)
            self.positions[symbol]['avg_price'] = total_cost / total_qty
            self.positions[symbol]['quantity'] = total_qty
        else:
            self.positions[symbol] = {'quantity': quantity, 'avg_price': price}
        
        # Create trade
        trade = Trade(symbol, 'BUY', quantity, price, date)
        self.trades.append(trade)
        self.logger.info(f"BUY {quantity} {symbol} @ {price:.2f}, Cost: {cost:.2f}")
        return True
    
    def sell(self, symbol: str, quantity: int, price: float, date: datetime) -> bool:
        """Execute sell order"""
        if symbol not in self.positions or self.positions[symbol]['quantity'] < quantity:
            self.logger.warning(f"Insufficient position to sell {quantity} {symbol}")
            return False
        
        proceeds = quantity * price * (1 - self.commission)
        self.cash += proceeds
        
        # Update position
        self.positions[symbol]['quantity'] -= quantity
        if self.positions[symbol]['quantity'] == 0:
            del self.positions[symbol]
        
        # Close corresponding trade
        commission_total = quantity * price * self.commission
        trade = Trade(symbol, 'SELL', quantity, price, date)
        trade.close_trade(price, date, commission_total)
        self.trades.append(trade)
        
        self.logger.info(f"SELL {quantity} {symbol} @ {price:.2f}, Proceeds: {proceeds:.2f}")
        return True
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        value = self.cash
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                value += pos['quantity'] * current_prices[symbol]
        return value
    
    def get_equity_curve(self, price_data: pd.DataFrame) -> pd.Series:
        """Generate equity curve"""
        equity = []
        dates = price_data.index
        for i, date in enumerate(dates):
            current_prices = {symbol: price_data.iloc[i]['close'] for symbol in [price_data.attrs.get('symbol', '')] if symbol}
            equity.append(self.get_portfolio_value(current_prices))
        return pd.Series(equity, index=dates)
