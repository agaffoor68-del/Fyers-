#!/usr/bin/env python3
"""
Quick test script for Fyers API
"""
from src.executors.fyers_client import get_fyers_client
from src.data.fyers_data_fetcher import fetch_candles
from src.executors.live_feed import start_live_feed

def test_connection():
    try:
        fyers = get_fyers_client()
        print("Fyers client initialized successfully!")
        return fyers
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_data_fetch(fyers):
    if fyers:
        candles = fetch_candles(fyers, symbol="NSE:SBIN-EQ", resolution="5", days=5)
        print(f"Fetched {len(candles)} candles")
        return candles
    return []

def test_live_feed(fyers):
    if fyers:
        feed = start_live_feed(fyers)
        print("Live feed test completed")

if __name__ == "__main__":
    print("Testing Fyers Integration...")
    fyers = test_connection()
    test_data_fetch(fyers)
    test_live_feed(fyers)
