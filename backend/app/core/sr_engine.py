import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("SREngine")


class SREngine:
    """
    Support & Resistance engine.
    Calculates:
      - Pivot Points (Standard, Fibonacci, Camarilla, Woodie)
      - Fibonacci Retracements
      - Local Min/Max Pivots (swing highs/lows)
    """

    def __init__(self):
        self.logger = logger

    def calculate_pivot_points(
        self, high: float, low: float, close: float, method: str = "standard"
    ) -> Dict[str, float]:
        """
        Calculate pivot point levels.

        Standard:
          P = (H + L + C) / 3
          R1 = 2*P - L
          S1 = 2*P - H
          R2 = P + (H - L)
          S2 = P - (H - L)
          R3 = H + 2*(P - L)
          S3 = L - 2*(H - P)

        Fibonacci:
          P = (H + L + C) / 3
          R1 = P + 0.382*(H - L)
          S1 = P - 0.382*(H - L)
          R2 = P + 0.618*(H - L)
          S2 = P - 0.618*(H - L)
          R3 = P + 1.0*(H - L)
          S3 = P - 1.0*(H - L)

        Camarilla:
          P = (H + L + C) / 3
          R1 = C + (H - L) * 1.1 / 12
          S1 = C - (H - L) * 1.1 / 12
          R2 = C + (H - L) * 1.1 / 6
          S2 = C - (H - L) * 1.1 / 6
          R3 = C + (H - L) * 1.1 / 4
          S3 = C - (H - L) * 1.1 / 4
          R4 = C + (H - L) * 1.1 / 2
          S4 = C - (H - L) * 1.1 / 2

        Woodie:
          P = (H + L + 2*C) / 4
          R1 = 2*P - L
          S1 = 2*P - H
          R2 = P + H - L
          S2 = P - H + L
        """
        try:
            if method == "fibonacci":
                p = (high + low + close) / 3
                diff = high - low
                return {
                    "P": round(p, 2),
                    "R1": round(p + 0.382 * diff, 2),
                    "S1": round(p - 0.382 * diff, 2),
                    "R2": round(p + 0.618 * diff, 2),
                    "S2": round(p - 0.618 * diff, 2),
                    "R3": round(p + 1.0 * diff, 2),
                    "S3": round(p - 1.0 * diff, 2),
                    "method": "fibonacci",
                }
            elif method == "camarilla":
                p = (high + low + close) / 3
                diff = high - low
                return {
                    "P": round(p, 2),
                    "R1": round(close + diff * 1.1 / 12, 2),
                    "S1": round(close - diff * 1.1 / 12, 2),
                    "R2": round(close + diff * 1.1 / 6, 2),
                    "S2": round(close - diff * 1.1 / 6, 2),
                    "R3": round(close + diff * 1.1 / 4, 2),
                    "S3": round(close - diff * 1.1 / 4, 2),
                    "R4": round(close + diff * 1.1 / 2, 2),
                    "S4": round(close - diff * 1.1 / 2, 2),
                    "method": "camarilla",
                }
            elif method == "woodie":
                p = (high + low + 2 * close) / 4
                return {
                    "P": round(p, 2),
                    "R1": round(2 * p - low, 2),
                    "S1": round(2 * p - high, 2),
                    "R2": round(p + high - low, 2),
                    "S2": round(p - high + low, 2),
                    "method": "woodie",
                }
            else:  # standard
                p = (high + low + close) / 3
                return {
                    "P": round(p, 2),
                    "R1": round(2 * p - low, 2),
                    "S1": round(2 * p - high, 2),
                    "R2": round(p + (high - low), 2),
                    "S2": round(p - (high - low), 2),
                    "R3": round(high + 2 * (p - low), 2),
                    "S3": round(low - 2 * (high - p), 2),
                    "method": "standard",
                }
        except Exception as e:
            self.logger.error(f"Error calculating pivot points: {e}")
            return {}

    def calculate_fibonacci_retracements(
        self, high: float, low: float
    ) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels.
        For an uptrend: levels are drawn from low to high.
        For a downtrend: levels are drawn from high to low.
        """
        try:
            diff = high - low
            return {
                "0%": round(high, 2),
                "23.6%": round(high - 0.236 * diff, 2),
                "38.2%": round(high - 0.382 * diff, 2),
                "50%": round(high - 0.5 * diff, 2),
                "61.8%": round(high - 0.618 * diff, 2),
                "78.6%": round(high - 0.786 * diff, 2),
                "100%": round(low, 2),
                "high": round(high, 2),
                "low": round(low, 2),
            }
        except Exception as e:
            self.logger.error(f"Error calculating Fibonacci retracements: {e}")
            return {}

    def calculate_local_pivots(
        self,
        df: pd.DataFrame,
        left_bars: int = 10,
        right_bars: int = 10,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Find local swing highs (resistance) and swing lows (support).
        A bar is a swing high if its high is the highest in the window
        [i-left_bars, i+right_bars]. A bar is a swing low if its low is
        the lowest in that window.

        Returns:
            (resistance_levels, support_levels) - each a list of dicts
            with price, timestamp, and strength.
        """
        try:
            highs = df["high"].values
            lows = df["low"].values
            timestamps = df.index.values

            resistance = []
            support = []

            n = len(df)
            for i in range(left_bars, n - right_bars):
                window_highs = highs[i - left_bars : i + right_bars + 1]
                window_lows = lows[i - left_bars : i + right_bars + 1]

                # Swing high: current high is the max in window
                if highs[i] == window_highs.max():
                    # Count how many times this level is touched (strength)
                    touches = int((window_highs >= highs[i] * 0.999).sum())
                    resistance.append({
                        "price": round(float(highs[i]), 2),
                        "timestamp": str(timestamps[i]),
                        "strength": touches,
                        "type": "resistance",
                    })

                # Swing low: current low is the min in window
                if lows[i] == window_lows.min():
                    touches = int((window_lows <= lows[i] * 1.001).sum())
                    support.append({
                        "price": round(float(lows[i]), 2),
                        "timestamp": str(timestamps[i]),
                        "strength": touches,
                        "type": "support",
                    })

            # Merge nearby levels (within 0.5% of each other)
            resistance = self._merge_levels(resistance)
            support = self._merge_levels(support)

            # Sort by strength desc, then price
            resistance.sort(key=lambda x: (-x["strength"], x["price"]))
            support.sort(key=lambda x: (-x["strength"], x["price"]))

            return resistance[:10], support[:10]
        except Exception as e:
            self.logger.error(f"Error calculating local pivots: {e}")
            return [], []

    def _merge_levels(
        self, levels: List[Dict[str, Any]], tolerance: float = 0.005
    ) -> List[Dict[str, Any]]:
        """Merge nearby price levels within tolerance (default 0.5%)."""
        if not levels:
            return []

        sorted_levels = sorted(levels, key=lambda x: x["price"])
        merged = [sorted_levels[0]]

        for level in sorted_levels[1:]:
            last = merged[-1]
            if abs(level["price"] - last["price"]) / last["price"] <= tolerance:
                # Merge: keep the stronger one, average price
                last["price"] = round((last["price"] + level["price"]) / 2, 2)
                last["strength"] = max(last["strength"], level["strength"])
            else:
                merged.append(level)

        return merged

    def calculate_sr_levels(
        self,
        df: pd.DataFrame,
        pivot_method: str = "standard",
        fib_length: int = 50,
        local_left: int = 10,
        local_right: int = 10,
    ) -> Dict[str, Any]:
        """
        Calculate all S&R levels and return as JSON-serializable dict.

        Args:
            df: OHLCV DataFrame
            pivot_method: "standard", "fibonacci", "camarilla", "woodie"
            fib_length: lookback for Fibonacci high/low
            local_left: left bars for local pivots
            local_right: right bars for local pivots

        Returns:
            Dict with pivot_points, fibonacci, local_resistance, local_support
        """
        try:
            result: Dict[str, Any] = {
                "pivot_points": {},
                "fibonacci": {},
                "local_resistance": [],
                "local_support": [],
            }

            if df is None or df.empty:
                return result

            # Use the last complete candle for pivot points
            last = df.iloc[-1]
            high = float(last["high"])
            low = float(last["low"])
            close = float(last["close"])

            # Pivot points
            result["pivot_points"] = self.calculate_pivot_points(
                high, low, close, method=pivot_method
            )

            # Fibonacci using lookback window
            if len(df) >= fib_length:
                window = df.tail(fib_length)
                fib_high = float(window["high"].max())
                fib_low = float(window["low"].min())
                result["fibonacci"] = self.calculate_fibonacci_retracements(
                    fib_high, fib_low
                )
                result["fibonacci"]["lookback_high"] = fib_high
                result["fibonacci"]["lookback_low"] = fib_low
                result["fibonacci"]["lookback_period"] = fib_length

            # Local pivots
            local_res, local_sup = self.calculate_local_pivots(
                df, left_bars=local_left, right_bars=local_right
            )
            result["local_resistance"] = local_res
            result["local_support"] = local_sup

            return result
        except Exception as e:
            self.logger.error(f"Error calculating S&R levels: {e}")
            return {
                "pivot_points": {},
                "fibonacci": {},
                "local_resistance": [],
                "local_support": [],
            }
