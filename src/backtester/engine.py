import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from src.backtester.portfolio import Portfolio, Trade
from src.strategies.base_strategy import BaseStrategy
from src.config.trading_config import TradingConfig, BacktestConfig
from src.utils.logger import get_logger

class Backtester:
    """Main backtesting engine"""
    
    def __init__(self, data: pd.DataFrame, strategy: BaseStrategy, 
                 initial_capital: float = 100000.0,
                 commission: float = 0.0003,
                 slippage: float = 0.0001,
                 config: Optional[TradingConfig] = None):
        self.data = data.copy()
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.config = config or TradingConfig()
        self.portfolio = Portfolio(initial_capital, commission)
        self.logger = get_logger("Backtester")
        self.results = {}
        self.equity_curve = []
        
    def run(self) -> Dict:
        """Run backtest"""
        self.logger.info(f"Starting backtest for {self.strategy.name}")
        self.logger.info(f"Initial Capital: {self.initial_capital}")
        
        # Generate signals
        signal_data = self.strategy.generate_signals(self.data)
        symbol = self.data.attrs.get('symbol', 'SYMBOL')
        
        # Iterate through data
        for i in range(len(signal_data)):
            date = signal_data.index[i]
            row = signal_data.iloc[i]
            price = row['close']
            
            # Apply slippage
            buy_price = price * (1 + self.slippage)
            sell_price = price * (1 - self.slippage)
            
            signal = row.get('signal', 0)
            
            if signal == 1:  # Buy signal
                # Calculate position size (simple: use available cash)
                available_cash = self.portfolio.cash
                quantity = int(available_cash / buy_price)
                if quantity > 0:
                    self.portfolio.buy(symbol, quantity, buy_price, date)
            
            elif signal == -1:  # Sell signal
                position = self.portfolio.get_position(symbol)
                if position['quantity'] > 0:
                    self.portfolio.sell(symbol, position['quantity'], sell_price, date)
            
            # Track equity
            current_prices = {symbol: price}
            portfolio_value = self.portfolio.get_portfolio_value(current_prices)
            self.equity_curve.append({
                'date': date,
                'equity': portfolio_value,
                'cash': self.portfolio.cash
            })
        
        # Close any remaining positions
        if symbol and symbol in self.portfolio.positions:
            final_price = signal_data.iloc[-1]['close'] * (1 - self.slippage)
            position = self.portfolio.positions[symbol]
            self.portfolio.sell(symbol, position['quantity'], final_price, signal_data.index[-1])
        
        self.results = self.calculate_metrics()
        self.logger.info("Backtest completed")
        return self.results
    
    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.equity_curve:
            return {}
        
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df.set_index('date', inplace=True)
        
        initial_equity = self.initial_capital
        final_equity = equity_df['equity'].iloc[-1]
        
        total_return = (final_equity - initial_equity) / initial_equity * 100
        total_pnl = final_equity - initial_equity
        
        # Calculate returns
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        # Sharpe Ratio (assuming risk-free rate 0)
        returns = equity_df['returns'].dropna()
        if len(returns) > 0 and returns.std() != 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # Max Drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax'] * 100
        max_drawdown = equity_df['drawdown'].min()
        
        # Trade statistics
        total_trades = len([t for t in self.portfolio.trades if t.status == 'CLOSED'])
        winning_trades = len([t for t in self.portfolio.trades if t.status == 'CLOSED' and t.pnl > 0])
        losing_trades = len([t for t in self.portfolio.trades if t.status == 'CLOSED' and t.pnl < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate profit factor
        gross_profit = sum([t.pnl for t in self.portfolio.trades if t.status == 'CLOSED' and t.pnl > 0])
        gross_loss = abs(sum([t.pnl for t in self.portfolio.trades if t.status == 'CLOSED' and t.pnl < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        metrics = {
            'initial_capital': initial_equity,
            'final_equity': final_equity,
            'total_return_pct': total_return,
            'total_pnl': total_pnl,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate_pct': win_rate,
            'profit_factor': profit_factor,
            'equity_curve': equity_df
        }
        
        return metrics
    
    def print_results(self):
        """Print backtest results"""
        if not self.results:
            self.run()
        
        print("\n" + "="*50)
        print(f"BACKTEST RESULTS - {self.strategy.name}")
        print("="*50)
        print(f"Initial Capital: ₹{self.results['initial_capital']:,.2f}")
        print(f"Final Equity:     ₹{self.results['final_equity']:,.2f}")
        print(f"Total PnL:        ₹{self.results['total_pnl']:,.2f}")
        print(f"Total Return:     {self.results['total_return_pct']:.2f}%")
        print("-"*50)
        print(f"Sharpe Ratio:     {self.results['sharpe_ratio']:.3f}")
        print(f"Max Drawdown:     {self.results['max_drawdown_pct']:.2f}%")
        print("-"*50)
        print(f"Total Trades:     {self.results['total_trades']}")
        print(f"Winning Trades:   {self.results['winning_trades']}")
        print(f"Losing Trades:    {self.results['losing_trades']}")
        print(f"Win Rate:         {self.results['win_rate_pct']:.2f}%")
        print(f"Profit Factor:    {self.results['profit_factor']:.3f}")
        print("="*50 + "\n")
    
    def get_trades_report(self) -> pd.DataFrame:
        """Get detailed trades report"""
        trades_data = []
        for trade in self.portfolio.trades:
            if trade.status == 'CLOSED':
                trades_data.append({
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'quantity': trade.quantity,
                    'entry_price': trade.entry_price,
                    'entry_date': trade.entry_date,
                    'exit_price': trade.exit_price,
                    'exit_date': trade.exit_date,
                    'pnl': trade.pnl,
                    'pnl_pct': trade.pnl_pct,
                    'commission': trade.commission
                })
        return pd.DataFrame(trades_data)
