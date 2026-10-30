from fyers_apiv3 import fyersModel
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

load_dotenv()


class FyersService:
    def __init__(self):
        self.client_id = os.getenv("FYERS_CLIENT_ID")
        self.access_token = os.getenv("FYERS_ACCESS_TOKEN")
        self.client_secret = os.getenv("FYERS_CLIENT_SECRET")
        self._fyers = None

    @property
    def fyers(self):
        if self._fyers is None:
            if not self.client_id or not self.access_token:
                raise ValueError("Fyers credentials not configured")
            self._fyers = fyersModel.FyersModel(
                client_id=self.client_id,
                token=self.access_token,
                is_async=False,
                log_path=""
            )
        return self._fyers

    def get_profile(self) -> Dict[str, Any]:
        """Get user profile"""
        try:
            return self.fyers.get_profile()
        except Exception as e:
            return {"error": str(e)}

    def get_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """Get live quotes for symbols"""
        try:
            data = {"symbols": ",".join(symbols)}
            return self.fyers.quotes(data=data)
        except Exception as e:
            return {"error": str(e)}

    def fetch_candles(self, symbol: str = "NSE:SBIN-EQ", resolution: str = "5",
                      days: int = 15) -> List[List]:
        """Fetch historical candle data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = {
                "symbol": symbol,
                "resolution": resolution,
                "date_format": "1",
                "range_from": start_date.strftime("%Y-%m-%d"),
                "range_to": end_date.strftime("%Y-%m-%d"),
                "cont_flag": "1"
            }
            response = self.fyers.history(data=data)
            if response.get("s") == "ok":
                return response.get("candles", [])
            return []
        except Exception as e:
            print(f"Error fetching candles: {e}")
            return []

    def place_order(self, symbol: str, side: str, quantity: int,
                    order_type: str = "MARKET", price: float = 0,
                    stop_price: float = 0, validity: str = "DAY") -> Dict[str, Any]:
        """Place a live order"""
        try:
            data = {
                "symbol": symbol,
                "qty": quantity,
                "type": order_type,
                "side": side.upper(),
                "productType": "INTRADAY",
                "validity": validity,
                "disclosedQty": 0,
                "offlineOrder": False,
                "stopLoss": stop_price,
                "takeProfit": 0,
                "price": price
            }
            return self.fyers.place_order(data=data)
        except Exception as e:
            return {"error": str(e)}

    def get_orderbook(self) -> Dict[str, Any]:
        """Get order book"""
        try:
            return self.fyers.orderbook()
        except Exception as e:
            return {"error": str(e)}

    def get_positions(self) -> Dict[str, Any]:
        """Get positions"""
        try:
            return self.fyers.positions()
        except Exception as e:
            return {"error": str(e)}

    def get_funds(self) -> Dict[str, Any]:
        """Get funds/margin"""
        try:
            return self.fyers.funds()
        except Exception as e:
            return {"error": str(e)}
