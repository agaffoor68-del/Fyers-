from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()


class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String)  # BUY/SELL
    quantity = Column(Float)
    entry_price = Column(Float)
    exit_price = Column(Float)
    pnl = Column(Float)
    pnl_percent = Column(Float)
    strategy_name = Column(String)
    status = Column(String)  # OPEN/CLOSED
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    rules = Column(JSON)
    indicators = Column(JSON)
    win_rate = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    is_active = Column(Boolean, default=False)
    is_paper = Column(Boolean, default=True)
    created_by = Column(String, default="grok_ai")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String)
    quantity = Column(Float)
    entry_price = Column(Float)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    status = Column(String, default="OPEN")  # OPEN/CLOSED/STOPPED
    pnl = Column(Float, default=0.0)
    strategy_id = Column(Integer, nullable=True)
    reason_closed = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)  # user/assistant/system
    message = Column(Text)
    context = Column(JSON)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class AILearningLog(Base):
    __tablename__ = "ai_learning_log"

    id = Column(Integer, primary_key=True, index=True)
    mistake_context = Column(Text)
    strategy_used = Column(String)
    reason_failed = Column(String)
    market_conditions = Column(JSON)
    lesson_learned = Column(Text)
    improvement_applied = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
