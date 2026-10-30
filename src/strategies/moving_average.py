import pandas as pd
import numpy as np
from src.strategies.base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    """Simple Moving Average Crossover Strategy"""
    
    def __init__(self, short_window: int = 10, long_window: int = 50, name: str = "MovingAverageCrossover"):
        super().__init__(name)
        self.short_window = short_window
        self.long_window = long_window
        self.set_params(short_window=short_window, long_window=long_window)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on MA crossover"""
        df = data.copy()
        
        # Calculate moving averages
        df['SMA_short'] = df['close'].rolling(window=self.short_window).mean()
        df['SMA_long'] = df['close'].rolling(window=self.long_window).mean()
        
        # Generate signals
        df['signal'] = 0
        df['position'] = df['SMA_short'] > df['SMA_long']
        df['position'] = df['position'].astype(int)
        
        # Signal when position changes
        df['prev_position'] = df['position'].shift(1)
        df['signal'] = 0
        df.loc[(df['position'] == 1) & (df['prev_position'] == 0), 'signal'] = 1  # Buy
        df.loc[(df['position'] == 0) & (df['prev_position'] == 1), 'signal'] = -1  # Sell
        
        return df
