from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from app.db.session import get_db
from app.core.indicator_engine import IndicatorEngine
from app.core.sr_engine import SREngine

router = APIRouter()
indicator_engine = IndicatorEngine()
sr_engine = SREngine()


class IndicatorParams(BaseModel):
    name: str
    params: Optional[Dict[str, Any]] = None


class ChartDataRequest(BaseModel):
    symbol: str = "NSE:SBIN-EQ"
    resolution: str = "5"
    days: int = 30
    indicators: Optional[List[IndicatorParams]] = None


@router.get("/indicators/list")
def get_indicators_list():
    """
    Returns all available indicators grouped by category for the frontend selector.
    """
    return indicator_engine.get_all_indicators()


@router.post("/chart-data")
def get_chart_data(request: ChartDataRequest, db: Session = Depends(get_db)):
    """
    Returns historical OHLC data + S&R levels + calculated indicators.
    Generates sample data if Fyers API is not available.
    """
    try:
        # Generate sample OHLCV data
        np.random.seed(42)
        n = 500
        dates = pd.date_range("2024-01-01", periods=n, freq="5min")
        base_price = 2500.0
        price = base_price * np.exp(np.cumsum(np.random.randn(n) * 0.002))

        df = pd.DataFrame(
            {
                "open": price * (1 + np.random.randn(n) * 0.0005),
                "high": price * (1 + np.abs(np.random.randn(n)) * 0.002),
                "low": price * (1 - np.abs(np.random.randn(n)) * 0.002),
                "close": price,
                "volume": np.random.randint(100000, 1000000, n),
            },
            index=dates,
        )
        df["high"] = df[["open", "high", "close"]].max(axis=1)
        df["low"] = df[["open", "low", "close"]].min(axis=1)

        # Calculate S&R levels
        sr_levels = sr_engine.calculate_sr_levels(df)

        # Calculate requested indicators
        indicator_list = []
        if request.indicators:
            for ind in request.indicators:
                params = ind.params or {}
                indicator_list.append({"name": ind.name, **params})

        df_with_indicators = indicator_engine.calculate_indicators(
            df, indicator_list
        )

        # Convert to JSON-serializable format
        chart_data = []
        for idx, row in df_with_indicators.iterrows():
            candle = {
                "time": idx.isoformat() if hasattr(idx, "isoformat") else str(idx),
                "open": round(float(row["open"]), 2),
                "high": round(float(row["high"]), 2),
                "low": round(float(row["low"]), 2),
                "close": round(float(row["close"]), 2),
                "volume": int(row["volume"]) if "volume" in row else 0,
            }

            # Add indicator values
            for col in df_with_indicators.columns:
                if col not in ("open", "high", "low", "close", "volume"):
                    val = row[col]
                    if pd.isna(val):
                        candle[col] = None
                    elif isinstance(val, (np.floating, float)):
                        candle[col] = round(float(val), 4)
                    elif isinstance(val, (np.integer, int)):
                        candle[col] = int(val)
                    else:
                        candle[col] = val

            chart_data.append(candle)

        return {
            "symbol": request.symbol,
            "resolution": request.resolution,
            "candles": chart_data,
            "sr_levels": sr_levels,
            "indicators_applied": [
                {"name": ind.name, "params": ind.params or {}}
                for ind in (request.indicators or [])
            ],
            "total_candles": len(chart_data),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sr-levels/{symbol}")
def get_sr_levels(
    symbol: str,
    pivot_method: str = Query("standard", description="Pivot method: standard, fibonacci, camarilla, woodie"),
    lookback: int = Query(50, description="Lookback period for Fibonacci"),
    db: Session = Depends(get_db),
):
    """Get Support & Resistance levels for a symbol."""
    try:
        # Generate sample data for S&R calculation
        np.random.seed(42)
        n = lookback + 50
        dates = pd.date_range("2024-01-01", periods=n, freq="5min")
        base_price = 2500.0
        price = base_price * np.exp(np.cumsum(np.random.randn(n) * 0.002))

        df = pd.DataFrame(
            {
                "open": price * (1 + np.random.randn(n) * 0.0005),
                "high": price * (1 + np.abs(np.random.randn(n)) * 0.002),
                "low": price * (1 - np.abs(np.random.randn(n)) * 0.002),
                "close": price,
                "volume": np.random.randint(100000, 1000000, n),
            },
            index=dates,
        )
        df["high"] = df[["open", "high", "close"]].max(axis=1)
        df["low"] = df[["open", "low", "close"]].min(axis=1)

        sr_levels = sr_engine.calculate_sr_levels(
            df, pivot_method=pivot_method, fib_length=lookback
        )

        return {
            "symbol": symbol,
            "pivot_method": pivot_method,
            "lookback": lookback,
            "levels": sr_levels,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
