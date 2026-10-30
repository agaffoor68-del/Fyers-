from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.models import PaperTrade, AILearningLog, Strategy
from app.grok_ai.strategy_builder import StrategyBuilder
from app.core.indicator_engine import IndicatorEngine
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger("PaperTradeService")


class PaperTradeService:
    def __init__(self, db: Session):
        self.db = db
        self.strategy_builder = StrategyBuilder()
        self.indicator_engine = IndicatorEngine()

    def execute_paper_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float,
        stop_loss: float = None,
        take_profit: float = None,
        strategy_id: int = None,
    ):
        trade = PaperTrade(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy_id=strategy_id,
            status="OPEN",
        )
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)
        return trade

    def check_stop_loss_take_profit(self, trade: PaperTrade, current_price: float):
        """Check if SL/TP hit and log to AILearningLog if failed"""
        if trade.status != "OPEN":
            return {"closed": False}

        should_close = False
        reason = None

        if trade.side == "BUY":
            if trade.stop_loss and current_price <= trade.stop_loss:
                should_close = True
                reason = "Stop Loss Hit"
            elif trade.take_profit and current_price >= trade.take_profit:
                should_close = True
                reason = "Take Profit Hit"
        elif trade.side == "SELL":
            if trade.stop_loss and current_price >= trade.stop_loss:
                should_close = True
                reason = "Stop Loss Hit"
            elif trade.take_profit and current_price <= trade.take_profit:
                should_close = True
                reason = "Take Profit Hit"

        if should_close:
            if trade.side == "BUY":
                pnl = (current_price - trade.entry_price) * trade.quantity
            else:
                pnl = (trade.entry_price - current_price) * trade.quantity

            trade.status = "STOPPED" if reason == "Stop Loss Hit" else "CLOSED"
            trade.exit_price = current_price
            trade.pnl = pnl
            trade.reason_closed = reason
            trade.closed_at = datetime.now()

            # Push to AILearningLog if it failed (hit SL)
            if reason == "Stop Loss Hit":
                strategy_name = "Unknown"
                if trade.strategy_id:
                    strategy = (
                        self.db.query(Strategy)
                        .filter(Strategy.id == trade.strategy_id)
                        .first()
                    )
                    if strategy:
                        strategy_name = strategy.name

                learning_log = AILearningLog(
                    mistake_context=f"Paper trade {trade.symbol} hit stop loss at {current_price}",
                    strategy_used=strategy_name,
                    reason_failed=self._classify_failure(pnl, trade),
                    market_conditions={
                        "current_price": current_price,
                        "entry_price": trade.entry_price,
                        "symbol": trade.symbol,
                        "side": trade.side,
                    },
                    lesson_learned=self._generate_lesson(pnl, trade, strategy_name),
                )
                self.db.add(learning_log)
                logger.info(
                    f"Logged AI learning: {strategy_name} - {reason} - PnL: {pnl}"
                )

            self.db.commit()
            return {"closed": True, "reason": reason, "pnl": pnl}

        return {"closed": False}

    def _classify_failure(self, pnl: float, trade: PaperTrade) -> str:
        """Classify the reason for failure"""
        loss_pct = abs(pnl) / (trade.entry_price * trade.quantity) * 100
        if loss_pct > 3.0:
            return "High Slippage"
        elif loss_pct > 1.5:
            return "False Breakout"
        else:
            return "Stop Loss Hit"

    def _generate_lesson(self, pnl: float, trade: PaperTrade, strategy_name: str) -> str:
        """Generate a lesson learned from the failed trade"""
        return (
            f"Review entry timing for {trade.symbol} using {strategy_name}. "
            f"Consider wider stop-loss or better confirmation indicators."
        )

    def run_strategy_on_data(
        self,
        df: pd.DataFrame,
        grok_strategy: Dict[str, Any],
        symbol: str = "NSE:SBIN-EQ",
        initial_capital: float = 100000.0,
    ) -> Dict[str, Any]:
        """
        Run a Grok-generated strategy on historical data, simulate trades,
        and log failures to AILearningLog.

        Args:
            df: OHLCV DataFrame
            grok_strategy: JSON strategy from Grok
            symbol: Trading symbol
            initial_capital: Starting capital

        Returns:
            Dict with backtest results and trade history
        """
        # Build signals using strategy builder
        df_signals, metadata = self.strategy_builder.build_strategy_from_grok(
            grok_strategy, df
        )

        # Add SL/TP levels
        df_signals = self.strategy_builder.generate_entry_exit_points(
            df_signals,
            stop_loss_pct=grok_strategy.get("stop_loss_pct", 2.0),
            take_profit_pct=grok_strategy.get("take_profit_pct", 4.0),
        )

        # Run simple backtest
        results = self.strategy_builder.backtest_signals(
            df_signals, initial_capital=initial_capital
        )

        # Simulate trades and log failures
        trades = []
        position = 0
        entry_price = 0
        entry_idx = None

        for i in range(len(df_signals)):
            row = df_signals.iloc[i]
            signal = row["signal"]
            close_price = row["close"]

            if signal == 1 and position == 0:  # Buy entry
                position = 1
                entry_price = close_price
                entry_idx = i
                quantity = (initial_capital * 0.1) / close_price  # 10% capital per trade
                self.execute_paper_trade(
                    symbol=symbol,
                    side="BUY",
                    quantity=quantity,
                    entry_price=close_price,
                    stop_loss=row.get("stop_loss"),
                    take_profit=row.get("take_profit"),
                    strategy_id=None,
                )
                trades.append(
                    {
                        "type": "BUY",
                        "price": close_price,
                        "date": row.name if hasattr(row, "name") else i,
                        "stop_loss": row.get("stop_loss"),
                        "take_profit": row.get("take_profit"),
                    }
                )

            elif signal == -1 and position == 1:  # Sell exit
                position = 0
                pnl = (close_price - entry_price) * ((initial_capital * 0.1) / entry_price)
                self.check_stop_loss_take_profit(
                    self.db.query(PaperTrade)
                    .filter(PaperTrade.symbol == symbol)
                    .order_by(PaperTrade.timestamp.desc())
                    .first(),
                    close_price,
                )
                trades.append(
                    {
                        "type": "SELL",
                        "price": close_price,
                        "date": row.name if hasattr(row, "name") else i,
                        "pnl": pnl,
                    }
                )
                entry_price = 0

        return {
            "strategy_metadata": metadata,
            "results": results,
            "trades": trades,
            "df_with_signals": df_signals,
        }
