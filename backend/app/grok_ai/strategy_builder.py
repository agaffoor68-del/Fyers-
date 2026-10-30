import pandas as pd
import numpy as np
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from app.core.indicator_engine import IndicatorEngine

logger = logging.getLogger("StrategyBuilder")


class StrategyBuilder:
    """
    Builds trading strategies from Grok AI's JSON output.
    Calculates indicators via IndicatorEngine and generates entry/exit signals.
    """

    def __init__(self):
        self.indicator_engine = IndicatorEngine()

    def build_strategy_from_grok(
        self,
        grok_response: Dict[str, Any],
        df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parse Grok's JSON strategy response, calculate indicators, and generate signals.

        Args:
            grok_response: JSON dict from Grok with keys:
                - strategy_name
                - indicators: [{"name": "rsi", "length": 14}, ...]
                - entry_logic: "RSI < 30 AND close > EMA_50"
                - exit_logic: "RSI > 70 OR close < EMA_50"
                - stop_loss_pct
                - take_profit_pct
            df: OHLCV DataFrame

        Returns:
            Tuple of (DataFrame with signals, strategy metadata dict)
        """
        strategy_name = grok_response.get("strategy_name", "Grok Strategy")
        indicators = grok_response.get("indicators", [])
        entry_logic = grok_response.get("entry_logic", "")
        exit_logic = grok_response.get("exit_logic", "")
        stop_loss_pct = grok_response.get("stop_loss_pct", 2.0)
        take_profit_pct = grok_response.get("take_profit_pct", 4.0)

        # Step 1: Calculate indicators on the dataframe
        df_enriched = self.indicator_engine.calculate_indicators(df, indicators)

        # Step 2: Generate entry/exit signals from logic strings
        df_signals = self._generate_signals(
            df_enriched, entry_logic, exit_logic
        )

        # Step 3: Build metadata
        metadata = {
            "strategy_name": strategy_name,
            "indicators": indicators,
            "entry_logic": entry_logic,
            "exit_logic": exit_logic,
            "stop_loss_pct": stop_loss_pct,
            "take_profit_pct": take_profit_pct,
            "indicator_columns": self.indicator_engine.get_indicator_columns(indicators),
        }

        return df_signals, metadata

    def _generate_signals(
        self,
        df: pd.DataFrame,
        entry_logic: str,
        exit_logic: str,
    ) -> pd.DataFrame:
        """
        Parse logic strings and generate buy/sell signal columns.

        Logic format examples:
        - "RSI < 30 AND close > EMA_50"
        - "MACD > MACDs AND close > BBU"
        - "RSI_14 > 70"
        """
        df = df.copy()
        df["signal"] = 0  # 0 = HOLD, 1 = BUY, -1 = SELL
        df["entry_signal"] = False
        df["exit_signal"] = False

        if entry_logic:
            entry_condition = self._parse_logic(entry_logic, df)
            if entry_condition is not None:
                df.loc[entry_condition, "signal"] = 1
                df.loc[entry_condition, "entry_signal"] = True

        if exit_logic:
            exit_condition = self._parse_logic(exit_logic, df)
            if exit_condition is not None:
                # Only exit if we have a position (signal was previously 1)
                df.loc[exit_condition, "signal"] = -1
                df.loc[exit_condition, "exit_signal"] = True

        return df

    def _parse_logic(self, logic: str, df: pd.DataFrame) -> Optional[pd.Series]:
        """
        Parse a logic string like "RSI < 30 AND close > EMA_50" into a boolean Series.

        Supports:
        - Comparison operators: <, >, <=, >=, ==, !=
        - Logical operators: AND, OR
        - Column references: RSI_14, EMA_50, close, high, low, MACD_12_26_9
        - Numeric values
        """
        if not logic or not logic.strip():
            return None

        try:
            # Normalize the logic string
            logic = logic.strip()

            # Replace AND/OR with Python equivalents
            expr = logic.replace(" AND ", " & ").replace(" OR ", " | ")

            # Find all column references (identifiers that are not operators or numbers)
            # Pattern: word characters and underscores
            tokens = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", expr)

            # Build a local namespace with column references
            local_ns = {}
            for token in tokens:
                if token.lower() in ("and", "or", "not", "true", "false", "none"):
                    continue
                if token.isdigit():
                    continue

                # Try to find the column in the dataframe
                if token in df.columns:
                    local_ns[token] = df[token]
                else:
                    # Try case-insensitive match
                    matched = False
                    for col in df.columns:
                        if col.lower() == token.lower():
                            local_ns[token] = df[col]
                            matched = True
                            break
                    if not matched:
                        self.logger.warning(
                            f"Column '{token}' not found in dataframe for logic: {logic}"
                        )
                        # Treat as False to avoid errors
                        local_ns[token] = pd.Series(False, index=df.index)

            # Evaluate the expression
            result = eval(expr, {"__builtins__": {}}, local_ns)

            if isinstance(result, pd.Series):
                return result.fillna(False)
            else:
                return pd.Series(result, index=df.index).fillna(False)

        except Exception as e:
            self.logger.error(f"Error parsing logic '{logic}': {str(e)}")
            return None

    def generate_entry_exit_points(
        self,
        df: pd.DataFrame,
        stop_loss_pct: float = 2.0,
        take_profit_pct: float = 4.0,
    ) -> pd.DataFrame:
        """
        Add stop-loss and take-profit levels to the dataframe based on signals.

        For BUY signals: SL = entry * (1 - sl_pct/100), TP = entry * (1 + tp_pct/100)
        For SELL signals: SL = entry * (1 + sl_pct/100), TP = entry * (1 - tp_pct/100)
        """
        df = df.copy()
        df["stop_loss"] = np.nan
        df["take_profit"] = np.nan
        df["position_size"] = 0.0

        buy_mask = df["signal"] == 1
        sell_mask = df["signal"] == -1

        if buy_mask.any():
            entry_prices = df.loc[buy_mask, "close"]
            df.loc[buy_mask, "stop_loss"] = entry_prices * (1 - stop_loss_pct / 100)
            df.loc[buy_mask, "take_profit"] = entry_prices * (1 + take_profit_pct / 100)
            df.loc[buy_mask, "position_size"] = 1.0  # Long

        if sell_mask.any():
            entry_prices = df.loc[sell_mask, "close"]
            df.loc[sell_mask, "stop_loss"] = entry_prices * (1 + stop_loss_pct / 100)
            df.loc[sell_mask, "take_profit"] = entry_prices * (1 - take_profit_pct / 100)
            df.loc[sell_mask, "position_size"] = -1.0  # Short

        return df

    def backtest_signals(
        self,
        df: pd.DataFrame,
        initial_capital: float = 100000.0,
        position_pct: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Simple vectorized backtest of the generated signals.
        """
        df = df.copy()
        df["returns"] = df["close"].pct_change()
        df["strategy_returns"] = df["position_size"].shift(1) * df["returns"]

        # Calculate cumulative returns
        df["cum_market_returns"] = (1 + df["returns"]).cumprod()
        df["cum_strategy_returns"] = (1 + df["strategy_returns"].fillna(0)).cumprod()

        # Performance metrics
        total_return = (df["cum_strategy_returns"].iloc[-1] - 1) * 100
        market_return = (df["cum_market_returns"].iloc[-1] - 1) * 100

        # Sharpe ratio (simplified, daily)
        strategy_daily_returns = df["strategy_returns"].fillna(0)
        if strategy_daily_returns.std() != 0:
            sharpe = (strategy_daily_returns.mean() / strategy_daily_returns.std()) * np.sqrt(252)
        else:
            sharpe = 0.0

        # Max drawdown
        cum_returns = df["cum_strategy_returns"]
        running_max = cum_returns.cummax()
        drawdown = (cum_returns - running_max) / running_max
        max_drawdown = drawdown.min() * 100

        # Win rate
        trade_returns = strategy_daily_returns[strategy_daily_returns != 0]
        win_rate = (trade_returns > 0).mean() * 100 if len(trade_returns) > 0 else 0.0

        total_trades = int((df["signal"] != 0).sum())

        return {
            "total_return_pct": round(total_return, 2),
            "market_return_pct": round(market_return, 2),
            "sharpe_ratio": round(sharpe, 3),
            "max_drawdown_pct": round(max_drawdown, 2),
            "win_rate_pct": round(win_rate, 2),
            "total_trades": total_trades,
            "final_equity": round(initial_capital * df["cum_strategy_returns"].iloc[-1], 2),
        }
