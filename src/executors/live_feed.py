from typing import Optional
import json
from src.utils.logger import get_logger


class FyersLiveFeed:
    """Live WebSocket feed for Fyers market data"""
    
    def __init__(self, fyers_client=None):
        self.fyers = fyers_client
        self.logger = get_logger("FyersLiveFeed")
        self.ws = None
        self.subscribed_symbols = []
        self.is_running = False
    
    def start_live_feed(self, symbols: list = None):
        """Start live feed (Implementation pending)"""
        print("Live feed starting... (Implementation pending)")
        self.logger.info("Live feed starting... (Implementation pending)")
        self.is_running = True
        if symbols:
            self.subscribed_symbols = symbols
        pass
    
    def stop_live_feed(self):
        """Stop live feed"""
        print("Live feed stopping...")
        self.logger.info("Live feed stopping...")
        self.is_running = False
        pass
    
    def subscribe(self, symbols: list):
        """Subscribe to symbols"""
        self.subscribed_symbols.extend(symbols)
        self.logger.info(f"Subscribed to {symbols}")
    
    def unsubscribe(self, symbols: list):
        """Unsubscribe from symbols"""
        for sym in symbols:
            if sym in self.subscribed_symbols:
                self.subscribed_symbols.remove(sym)
        self.logger.info(f"Unsubscribed from {symbols}")


def start_live_feed(fyers):
    """Standalone function to start live feed"""
    feed = FyersLiveFeed(fyers)
    feed.start_live_feed()
    return feed
