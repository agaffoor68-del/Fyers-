import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Union

class DateTimeUtils:
    @staticmethod
    def to_fyers_date_format(date: Union[str, datetime]) -> str:
        """Convert date to Fyers API format (YYYY-MM-DD)"""
        if isinstance(date, str):
            return date
        return date.strftime("%Y-%m-%d")
    
    @staticmethod
    def get_date_range(start_date: Union[str, datetime], end_date: Union[str, datetime]) -> tuple:
        """Get date range in Fyers format"""
        start = DateTimeUtils.to_fyers_date_format(start_date)
        end = DateTimeUtils.to_fyers_date_format(end_date)
        return start, end
    
    @staticmethod
    def is_trading_day(date: datetime) -> bool:
        """Check if it's a trading day (Mon-Fri)"""
        return date.weekday() < 5
    
    @staticmethod
    def get_trading_days(start_date: datetime, end_date: datetime) -> list:
        """Get list of trading days between dates"""
        days = []
        current = start_date
        while current <= end_date:
            if DateTimeUtils.is_trading_day(current):
                days.append(current)
            current += timedelta(days=1)
        return days
    
    @staticmethod
    def convert_timestamp_to_datetime(timestamp: int) -> datetime:
        """Convert Unix timestamp to datetime"""
        return datetime.fromtimestamp(timestamp)

class DataUtils:
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare dataframe"""
        df = df.copy()
        # Remove duplicates
        df = df.drop_duplicates()
        # Forward fill NaN values
        df = df.ffill()
        # Backward fill remaining NaN
        df = df.bfill()
        return df
    
    @staticmethod
    def resample_data(df: pd.DataFrame, timeframe: str = 'D') -> pd.DataFrame:
        """Resample OHLCV data"""
        ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        # Rename columns to lowercase if needed
        df_cols = {col.lower(): col for col in df.columns}
        if all(c in df_cols for c in ['open', 'high', 'low', 'close']):
            resampled = df.rename(columns=df_cols).resample(timeframe).agg(ohlc_dict)
            return resampled.dropna()
        return df
    
    @staticmethod
    def add_returns(df: pd.DataFrame, price_col: str = 'close') -> pd.DataFrame:
        """Add returns columns to dataframe"""
        df = df.copy()
        df['returns'] = df[price_col].pct_change()
        df['log_returns'] = np.log(df[price_col] / df[price_col].shift(1))
        return df
