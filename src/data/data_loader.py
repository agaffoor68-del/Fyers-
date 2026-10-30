import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from src.config.fyers_config import FyersConfig
from src.utils.logger import get_logger

class DataLoader:
    """Load historical data from Fyers API or local files"""
    
    def __init__(self, config: Optional[FyersConfig] = None):
        self.config = config or FyersConfig()
        self.logger = get_logger("DataLoader")
    
    def load_historical_data(self, symbol: str, start_date: str, end_date: str, 
                           timeframe: str = "D") -> pd.DataFrame:
        """
        Load historical data
        timeframe: '1', '5', '15', '30', '60', 'D'
        """
        self.logger.info(f"Loading data for {symbol} from {start_date} to {end_date}")
        
        # Try to load from local file first
        local_file = f"data/historical/{symbol.replace(':', '_')}_{start_date}_{end_date}.csv"
        try:
            df = pd.read_csv(local_file, index_col=0, parse_dates=True)
            self.logger.info(f"Loaded data from local file: {local_file}")
            df.attrs['symbol'] = symbol
            return df
        except FileNotFoundError:
            self.logger.info("Local file not found, generating sample data")
        
        # Generate sample data for testing
        df = self.generate_sample_data(symbol, start_date, end_date)
        df.attrs['symbol'] = symbol
        return df
    
    def generate_sample_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate sample OHLCV data for testing"""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        dates = pd.date_range(start=start, end=end, freq='D')
        # Remove weekends
        dates = dates[dates.weekday < 5]
        
        np.random.seed(42)
        n = len(dates)
        # Generate random walk for prices
        returns = np.random.randn(n) * 0.02
        price = 1000 * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'open': price * (1 + np.random.randn(n) * 0.001),
            'high': price * (1 + np.abs(np.random.randn(n)) * 0.01),
            'low': price * (1 - np.abs(np.random.randn(n)) * 0.01),
            'close': price,
            'volume': np.random.randint(100000, 1000000, n)
        }, index=dates)
        
        # Ensure high >= low and high >= open/close and low <= open/close
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        
        self.logger.info(f"Generated {len(df)} sample data points for {symbol}")
        return df
    
    def save_data(self, df: pd.DataFrame, filename: str):
        """Save data to CSV"""
        filepath = f"data/historical/{filename}"
        df.to_csv(filepath)
        self.logger.info(f"Data saved to {filepath}")
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote from Fyers API"""
        # Placeholder for Fyers API integration
        self.logger.info(f"Fetching quote for {symbol}")
        return {'symbol': symbol, 'ltp': 0, 'bid': 0, 'ask': 0}
