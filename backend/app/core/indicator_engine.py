import pandas as pd
import pandas_ta as ta
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("IndicatorEngine")


class IndicatorEngine:
    """
    Dynamic technical indicator engine using pandas_ta.
    Supports 130+ indicators configured via a list of dictionaries.
    """

    # Categorized indicator registry for frontend selector
    INDICATOR_CATEGORIES: Dict[str, Dict[str, Dict[str, Any]]] = {
        "Trend": {
            "sma": {"params": {"length": 20}, "overlay": True, "description": "Simple Moving Average"},
            "ema": {"params": {"length": 20}, "overlay": True, "description": "Exponential Moving Average"},
            "wma": {"params": {"length": 20}, "overlay": True, "description": "Weighted Moving Average"},
            "hma": {"params": {"length": 20}, "overlay": True, "description": "Hull Moving Average"},
            "vwma": {"params": {"length": 20}, "overlay": True, "description": "Volume Weighted Moving Average"},
            "macd": {"params": {"fast": 12, "slow": 26, "signal": 9}, "overlay": False, "description": "MACD"},
            "macd_hist": {"params": {"fast": 12, "slow": 26, "signal": 9}, "overlay": False, "description": "MACD Histogram"},
            "ppo": {"params": {"fast": 12, "slow": 26, "signal": 9}, "overlay": False, "description": "Percentage Price Oscillator"},
            "adx": {"params": {"length": 14}, "overlay": False, "description": "Average Directional Index"},
            "dpo": {"params": {"length": 20}, "overlay": False, "description": "Detrended Price Oscillator"},
            "trix": {"params": {"length": 18}, "overlay": False, "description": "TRIX"},
            "vi": {"params": {"length": 14}, "overlay": False, "description": "Vortex Indicator"},
            "aroon": {"params": {"length": 25}, "overlay": False, "description": "Aroon"},
            "supertrend": {"params": {"length": 10, "multiplier": 3.0}, "overlay": True, "description": "Supertrend"},
            "ichimoku": {"params": {"tenkan": 9, "kijun": 26, "senkou_a": 52, "senkou_b": 26}, "overlay": True, "description": "Ichimoku Cloud"},
            "midprice": {"params": {"length": 20}, "overlay": True, "description": "Midpoint Price"},
            "typprice": {"params": {}, "overlay": True, "description": "Typical Price"},
            "wclprice": {"params": {}, "overlay": True, "description": "Weighted Close Price"},
        },
        "Momentum": {
            "rsi": {"params": {"length": 14}, "overlay": False, "description": "Relative Strength Index"},
            "stoch": {"params": {"k": 14, "d": 3}, "overlay": False, "description": "Stochastic Oscillator"},
            "stochrsi": {"params": {"length": 14, "rsi": 14, "k": 3, "d": 3}, "overlay": False, "description": "Stochastic RSI"},
            "cci": {"params": {"length": 20}, "overlay": False, "description": "Commodity Channel Index"},
            "roc": {"params": {"length": 10}, "overlay": False, "description": "Rate of Change"},
            "mom": {"params": {"length": 10}, "overlay": False, "description": "Momentum"},
            "willr": {"params": {"length": 14}, "overlay": False, "description": "Williams %R"},
            "uo": {"params": {"fast": 7, "medium": 14, "slow": 28}, "overlay": False, "description": "Ultimate Oscillator"},
            "tsi": {"params": {"fast": 13, "slow": 25}, "overlay": False, "description": "True Strength Index"},
            "cmo": {"params": {"length": 14}, "overlay": False, "description": "Chande Momentum Oscillator"},
            "rocr": {"params": {"length": 10}, "overlay": False, "description": "Rate of Change Ratio"},
            "rocp": {"params": {"length": 10}, "overlay": False, "description": "Rate of Change Percentage"},
            "mfi": {"params": {"length": 14}, "overlay": False, "description": "Money Flow Index"},
            "fisher": {"params": {"length": 9}, "overlay": False, "description": "Fisher Transform"},
            "qstick": {"params": {"length": 14}, "overlay": False, "description": "QStick"},
        },
        "Volatility": {
            "bbands": {"params": {"length": 20, "std": 2.0}, "overlay": True, "description": "Bollinger Bands"},
            "atr": {"params": {"length": 14}, "overlay": False, "description": "Average True Range"},
            "kc": {"params": {"length": 20, "multiplier": 2.0}, "overlay": True, "description": "Keltner Channels"},
            "donchian": {"params": {"length": 20}, "overlay": True, "description": "Donchian Channels"},
            "natr": {"params": {"length": 14}, "overlay": False, "description": "Normalized ATR"},
            "tr": {"params": {}, "overlay": False, "description": "True Range"},
            "stddev": {"params": {"length": 20}, "overlay": False, "description": "Standard Deviation"},
            "variance": {"params": {"length": 20}, "overlay": False, "description": "Variance"},
        },
        "Volume": {
            "obv": {"params": {}, "overlay": False, "description": "On-Balance Volume"},
            "ad": {"params": {}, "overlay": False, "description": "Accumulation/Distribution Line"},
            "adosc": {"params": {"fast": 3, "slow": 10}, "overlay": False, "description": "Chaikin Oscillator"},
            "vwap": {"params": {}, "overlay": True, "description": "Volume Weighted Average Price"},
            "vwma": {"params": {"length": 20}, "overlay": True, "description": "Volume Weighted Moving Average"},
            "mfi": {"params": {"length": 14}, "overlay": False, "description": "Money Flow Index"},
            "cmf": {"params": {"fast": 20}, "overlay": False, "description": "Chaikin Money Flow"},
            "efi": {"params": {}, "overlay": False, "description": "Elder Force Index"},
            "nvi": {"params": {}, "overlay": False, "description": "Negative Volume Index"},
            "pvi": {"params": {}, "overlay": False, "description": "Positive Volume Index"},
        },
        "Support_Resistance": {
            "pivot_points": {"params": {"method": "standard"}, "overlay": True, "description": "Pivot Points (S&R)"},
            "fibonacci": {"params": {"length": 50}, "overlay": True, "description": "Fibonacci Retracements"},
            "local_pivots": {"params": {"left_bars": 10, "right_bars": 10}, "overlay": True, "description": "Local Min/Max Pivots"},
        },
        "Candlestick": {
            "cdl_doji": {"params": {}, "overlay": False, "description": "Doji"},
            "cdl_hammer": {"params": {}, "overlay": False, "description": "Hammer"},
            "cdl_engulfing": {"params": {}, "overlay": False, "description": "Engulfing Pattern"},
            "cdl_morning_star": {"params": {}, "overlay": False, "description": "Morning Star"},
            "cdl_evening_star": {"params": {}, "overlay": False, "description": "Evening Star"},
            "cdl_hanging_man": {"params": {}, "overlay": False, "description": "Hanging Man"},
            "cdl_shooting_star": {"params": {}, "overlay": False, "description": "Shooting Star"},
            "cdl_harami": {"params": {}, "overlay": False, "description": "Harami Pattern"},
            "cdl_piercing": {"params": {}, "overlay": False, "description": "Piercing Pattern"},
            "cdl_dark_cloud": {"params": {}, "overlay": False, "description": "Dark Cloud Cover"},
        },
    }

    # Mapping of indicator names to their pandas_ta output column patterns
    INDICATOR_COLUMN_MAP = {
        "sma": lambda params: [f"SMA_{params.get('length', 20)}"],
        "ema": lambda params: [f"EMA_{params.get('length', 20)}"],
        "wma": lambda params: [f"WMA_{params.get('length', 20)}"],
        "hma": lambda params: [f"HMA_{params.get('length', 20)}"],
        "vwma": lambda params: [f"VWMA_{params.get('length', 20)}"],
        "macd": lambda params: [
            f"MACD_{params.get('fast', 12)}_{params.get('slow', 26)}_{params.get('signal', 9)}",
            f"MACDh_{params.get('fast', 12)}_{params.get('slow', 26)}_{params.get('signal', 9)}",
            f"MACDs_{params.get('fast', 12)}_{params.get('slow', 26)}_{params.get('signal', 9)}",
        ],
        "macd_hist": lambda params: [f"MACDh_{params.get('fast', 12)}_{params.get('slow', 26)}_{params.get('signal', 9)}"],
        "ppo": lambda params: [f"PPO_{params.get('fast', 12)}_{params.get('slow', 26)}_{params.get('signal', 9)}"],
        "adx": lambda params: [f"ADX_{params.get('length', 14)}", f"DMP_{params.get('length', 14)}", f"DMN_{params.get('length', 14)}"],
        "dpo": lambda params: [f"DPO_{params.get('length', 20)}"],
        "trix": lambda params: [f"TRIX_{params.get('length', 18)}"],
        "vi": lambda params: [f"VI_+_{params.get('length', 14)}", f"VI_-_{params.get('length', 14)}"],
        "aroon": lambda params: [f"AROOND_{params.get('length', 25)}", f"AROONU_{params.get('length', 25)}", f"AROONOSC_{params.get('length', 25)}"],
        "supertrend": lambda params: [f"SUPERT_{params.get('length', 10)}_{params.get('multiplier', 3.0)}", f"SUPERTd_{params.get('length', 10)}_{params.get('multiplier', 3.0)}", f"SUPERTl_{params.get('length', 10)}_{params.get('multiplier', 3.0)}", f"SUPERTs_{params.get('length', 10)}_{params.get('multiplier', 3.0)}"],
        "ichimoku": lambda params: [f"ITS_{params.get('tenkan', 9)}", f"IKS_{params.get('kijun', 26)}", f"CHINOU_{params.get('kijun', 26)}", f"SPAN A_{params.get('tenkan', 9)}_{params.get('kijun', 26)}_{params.get('senkou_a', 52)}", f"SPAN B_{params.get('kijun', 26)}_{params.get('senkou_b', 26)}"],
        "midprice": lambda params: [f"MIDPRICE_{params.get('length', 20)}"],
        "typprice": lambda params: ["TYPPRICE"],
        "wclprice": lambda params: ["WCLPRICE"],
        "rsi": lambda params: [f"RSI_{params.get('length', 14)}"],
        "stoch": lambda params: [f"STOCHk_{params.get('k', 14)}_{params.get('d', 3)}", f"STOCHd_{params.get('k', 14)}_{params.get('d', 3)}"],
        "stochrsi": lambda params: [f"STOCHRSIk_{params.get('length', 14)}_{params.get('rsi', 14)}_{params.get('k', 3)}_{params.get('d', 3)}", f"STOCHRSId_{params.get('length', 14)}_{params.get('rsi', 14)}_{params.get('k', 3)}_{params.get('d', 3)}"],
        "cci": lambda params: [f"CCI_{params.get('length', 20)}"],
        "roc": lambda params: [f"ROC_{params.get('length', 10)}"],
        "mom": lambda params: [f"MOM_{params.get('length', 10)}"],
        "willr": lambda params: [f"WILR_{params.get('length', 14)}"],
        "uo": lambda params: [f"UO_{params.get('fast', 7)}_{params.get('medium', 14)}_{params.get('slow', 28)}"],
        "tsi": lambda params: [f"TSI_{params.get('fast', 13)}_{params.get('slow', 25)}"],
        "cmo": lambda params: [f"CMO_{params.get('length', 14)}"],
        "rocr": lambda params: [f"ROCR_{params.get('length', 10)}"],
        "rocp": lambda params: [f"ROCP_{params.get('length', 10)}"],
        "mfi": lambda params: [f"MFI_{params.get('length', 14)}"],
        "fisher": lambda params: [f"FISHER_{params.get('length', 9)}"],
        "qstick": lambda params: [f"QSTICK_{params.get('length', 14)}"],
        "bbands": lambda params: [f"BBL_{params.get('length', 20)}_{params.get('std', 2.0)}", f"BBM_{params.get('length', 20)}_{params.get('std', 2.0)}", f"BBU_{params.get('length', 20)}_{params.get('std', 2.0)}"],
        "atr": lambda params: [f"ATR_{params.get('length', 14)}"],
        "kc": lambda params: [f"KCE_{params.get('length', 20)}_{params.get('multiplier', 2.0)}", f"KCM_{params.get('length', 20)}_{params.get('multiplier', 2.0)}", f"KCL_{params.get('length', 20)}_{params.get('multiplier', 2.0)}"],
        "donchian": lambda params: [f"DCU_{params.get('length', 20)}", f"DCL_{params.get('length', 20)}", f"DCM_{params.get('length', 20)}"],
        "natr": lambda params: [f"NATR_{params.get('length', 14)}"],
        "tr": lambda params: ["TR"],
        "stddev": lambda params: [f"STDDEV_{params.get('length', 20)}"],
        "variance": lambda params: [f"VARIANCE_{params.get('length', 20)}"],
        "obv": lambda params: ["OBV"],
        "ad": lambda params: ["AD"],
        "adosc": lambda params: [f"ADOSC_{params.get('fast', 3)}_{params.get('slow', 10)}"],
        "vwap": lambda params: ["VWAP"],
        "cmf": lambda params: [f"CMF_{params.get('fast', 20)}"],
        "efi": lambda params: ["EFI"],
        "nvi": lambda params: ["NVI"],
        "pvi": lambda params: ["PVI"],
        "cdl_doji": lambda params: ["CDL_DOJI"],
        "cdl_hammer": lambda params: ["CDL_HAMMER"],
        "cdl_engulfing": lambda params: ["CDL_ENGULFING"],
        "cdl_morning_star": lambda params: ["CDL_MORNINGSTAR"],
        "cdl_evening_star": lambda params: ["CDL_EVENINGSTAR"],
        "cdl_hanging_man": lambda params: ["CDL_HANGINGMAN"],
        "cdl_shooting_star": lambda params: ["CDL_SHOOTINGSTAR"],
        "cdl_harami": lambda params: ["CDL_HARAMI"],
        "cdl_piercing": lambda params: ["CDL_PIERCING"],
        "cdl_dark_cloud": lambda params: ["CDL_DARKCLOUDCOVER"],
    }

    def __init__(self):
        self.logger = logger

    def get_all_indicators(self) -> Dict[str, Any]:
        """
        Returns all available indicators grouped by category.
        Each indicator includes default params, overlay flag, and description.
        """
        result = {}
        for category, indicators in self.INDICATOR_CATEGORIES.items():
            result[category] = []
            for name, info in indicators.items():
                result[category].append({
                    "name": name,
                    "default_params": info["params"],
                    "overlay": info["overlay"],
                    "description": info["description"],
                    "category": category,
                })
        return {
            "categories": result,
            "total_count": sum(len(v) for v in result.values()),
        }

    def calculate_indicators(
        self, df: pd.DataFrame, indicator_list: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Dynamically calculate technical indicators using pandas_ta.

        Args:
            df: DataFrame with OHLCV columns (open, high, low, close, volume)
            indicator_list: List of dicts like [{"name": "rsi", "length": 14}, ...]

        Returns:
            DataFrame with indicator columns appended
        """
        if df is None or df.empty:
            self.logger.warning("Empty DataFrame provided to indicator engine")
            return df

        df = df.copy()

        # Ensure required columns exist with correct names for pandas_ta
        col_map = {}
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ("open", "high", "low", "close", "volume"):
                col_map[col] = col_lower

        if col_map:
            df = df.rename(columns=col_map)

        required_cols = ["open", "high", "low", "close"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            self.logger.error(f"Missing required OHLC columns: {missing}")
            return df

        for indicator_config in indicator_list:
            try:
                name = indicator_config.get("name", "").lower()
                params = {
                    k: v for k, v in indicator_config.items() if k != "name"
                }

                if not name:
                    continue

                # Get the pandas_ta function
                if not hasattr(df.ta, name):
                    self.logger.warning(
                        f"Indicator '{name}' not available in pandas_ta"
                    )
                    continue

                ta_func = getattr(df.ta, name)

                # Call the indicator function with params
                result = ta_func(**params) if params else ta_func()

                if result is None:
                    continue

                # Handle single Series result
                if isinstance(result, pd.Series):
                    result.name = result.name or f"{name.upper()}_{params.get('length', '')}"
                    df = pd.concat([df, result], axis=1)

                # Handle DataFrame result (multi-column indicators like MACD, BBANDS)
                elif isinstance(result, pd.DataFrame):
                    for col in result.columns:
                        if col not in df.columns:
                            df[col] = result[col]

                self.logger.debug(
                    f"Calculated indicator: {name} with params {params}"
                )

            except Exception as e:
                self.logger.error(
                    f"Error calculating indicator {indicator_config.get('name', 'unknown')}: {str(e)}"
                )
                continue

        return df

    def get_indicator_columns(
        self, indicator_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Predict the column names that will be generated for a given indicator list.
        Useful for strategy builder to reference columns in logic strings.
        """
        columns = []
        for config in indicator_list:
            name = config.get("name", "").lower()
            params = {k: v for k, v in config.items() if k != "name"}

            if name in self.INDICATOR_COLUMN_MAP:
                columns.extend(self.INDICATOR_COLUMN_MAP[name](params))
            else:
                # Generic fallback: try to infer column name
                length = params.get("length", params.get("period", 14))
                columns.append(f"{name.upper()}_{length}")

        return columns

    def list_available_indicators(self) -> List[str]:
        """Return list of all available indicator names in pandas_ta"""
        available = set()
        for attr in dir(ta):
            if not attr.startswith("_") and callable(getattr(ta, attr, None)):
                available.add(attr)
        # Also check df.ta accessor
        for attr in dir(pd.DataFrame.ta):
            if not attr.startswith("_") and attr not in available:
                available.add(attr)
        return sorted(available)
