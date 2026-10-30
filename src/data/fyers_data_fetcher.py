from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from src.utils.logger import get_logger


class FyersDataFetcher:
    """Fetch historical candle data from Fyers API"""
    
    def __init__(self, fyers_client=None):
        self.fyers = fyers_client
        self.logger = get_logger("FyersDataFetcher")
    
    def fetch_candles(self, symbol: str = "NSE:SBIN-EQ", resolution: str = "5", 
                     days: int = 15, start_date: Optional[datetime] = None, 
                     end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch historical candles from Fyers API
        
        Args:
            symbol: Trading symbol (e.g., "NSE:SBIN-EQ")
            resolution: Candle resolution in minutes ('1', '5', '15', '30', '60') or 'D'
            days: Number of days of data to fetch (used if dates not provided)
            start_date: Start date
            end_date: End date
        """
        self.logger.info(f"Fetching {days} days of {resolution}min data for {symbol}...")
        
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=days)
        
        data = {
            "symbol": symbol,
            "resolution": resolution,
            "date_format": "1",
            "range_from": start_date.strftime("%Y-%m-%d"),
            "range_to": end_date.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }
        
        try:
            if self.fyers is None:
                self.logger.error("Fyers client not initialized")
                return []
                
            response = self.fyers.history(data=data)
            
            if response.get("s") == "ok":
                candles = response.get("candles", [])
                self.logger.info(f"Successfully fetched {len(candles)} candles")
                return candles
            else:
                self.logger.error(f"Data Fetch Error: {response.get('message', 'Unknown Error')}")
                print("Data Fetch Error:", response.get("message", "Unknown Error"))
                return []
        except Exception as e:
            self.logger.error(f"Exception while fetching candles: {e}")
            print(f"Error: {e}")
            return []
    
    def candles_to_dataframe(self, candles: List) -> pd.DataFrame:
        """
        Convert Fyers candles format to DataFrame
        Fyers candles format: [[timestamp, open, high, low, close, volume], ...]
        """
        if not candles:
            return pd.DataFrame()
        
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        df.index.name = 'datetime'
        return df


def fetch_candles(fyers, symbol="NSE:SBIN-EQ", resolution="5", days=15):
    """Standalone function to fetch candles"""
    fetcher = FyersDataFetcher(fyers)
    return fetcher.fetch_candles(symbol=symbol, resolution=resolution, days=days)
