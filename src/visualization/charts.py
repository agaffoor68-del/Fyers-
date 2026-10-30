import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict
import os

class Visualizer:
    """Visualization tools for backtesting results"""
    
    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
        sns.set_palette("husl")
    
    def plot_equity_curve(self, results: Dict, save_path: str = None):
        """Plot equity curve"""
        equity_df = results.get('equity_curve')
        if equity_df is None:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(equity_df.index, equity_df['equity'], linewidth=2, label='Portfolio Value')
        ax.axhline(y=results['initial_capital'], color='r', linestyle='--', 
                   label='Initial Capital', alpha=0.7)
        ax.set_title(f"Equity Curve - {results.get('strategy_name', 'Strategy')}", 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Portfolio Value (₹)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        plt.show()
    
    def plot_drawdown(self, results: Dict, save_path: str = None):
        """Plot drawdown"""
        equity_df = results.get('equity_curve')
        if equity_df is None:
            return
        
        fig, ax = plt.subplots(figsize(12, 4))
        ax.fill_between(equity_df.index, equity_df['drawdown'], 0, 
                        alpha=0.3, color='red')
        ax.plot(equity_df.index, equity_df['drawdown'], color='red', linewidth=1.5)
        ax.set_title('Drawdown', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        plt.show()
    
    def plot_trades(self, data: pd.DataFrame, trades_df: pd.DataFrame, save_path: str = None):
        """Plot trades on price chart"""
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(data.index, data['close'], label='Price', linewidth=1.5)
        
        for _, trade in trades_df.iterrows():
            if trade['side'] == 'BUY':
                ax.scatter(trade['entry_date'], trade['entry_price'], 
                          color='green', marker='^', s=100, label='Buy' if _ == 0 else "")
            elif trade['side'] == 'SELL':
                ax.scatter(trade['exit_date'], trade['exit_price'], 
                          color='red', marker='v', s=100, label='Sell' if _ == 0 else "")
        
        ax.set_title('Trade Signals', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        plt.show()
    
    def create_performance_report(self, results: Dict, trades_df: pd.DataFrame, save_dir: str = "reports"):
        """Create comprehensive performance report"""
        os.makedirs(save_dir, exist_ok=True)
        self.plot_equity_curve(results, f"{save_dir}/equity_curve.png")
        self.plot_drawdown(results, f"{save_dir}/drawdown.png")
        print(f"Performance report created in {save_dir}/")
