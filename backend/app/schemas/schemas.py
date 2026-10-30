from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


class TradeLogBase(BaseModel):
    symbol: str
    side: str
    quantity: float
    entry_price: float
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    strategy_name: Optional[str] = None
    status: str = "OPEN"


class TradeLogCreate(TradeLogBase):
    pass


class TradeLogOut(TradeLogBase):
    id: int
    timestamp: datetime
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    indicators: Optional[List[str]] = None
    win_rate: Optional[float] = 0.0
    total_trades: Optional[int] = 0
    is_active: Optional[bool] = False
    is_paper: Optional[bool] = True


class StrategyCreate(StrategyBase):
    pass


class StrategyOut(StrategyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaperTradeBase(BaseModel):
    symbol: str
    side: str
    quantity: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy_id: Optional[int] = None


class PaperTradeCreate(PaperTradeBase):
    pass


class PaperTradeOut(PaperTradeBase):
    id: int
    status: str = "OPEN"
    pnl: Optional[float] = 0.0
    reason_closed: Optional[str] = None
    timestamp: datetime
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AILearningLogBase(BaseModel):
    mistake_context: str
    strategy_used: str
    reason_failed: str
    market_conditions: Optional[Dict[str, Any]] = None
    lesson_learned: Optional[str] = None
    improvement_applied: Optional[bool] = False


class AILearningLogCreate(AILearningLogBase):
    pass


class AILearningLogOut(AILearningLogBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AIChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class AIChatResponse(BaseModel):
    response: str
    session_id: str


class AIChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class AIChatResponse(BaseModel):
    response: str
    session_id: str


class AutoOptimizeResponse(BaseModel):
    optimization: str
    status: str


class MemoryResponse(BaseModel):
    failures: List[Dict[str, Any]]
    count: int


class StrategyGenerateRequest(BaseModel):
    user_request: str
    symbol: str = "NSE:SBIN-EQ"
    days: int = 30
    resolution: str = "5"


class StrategyGenerateResponse(BaseModel):
    success: bool
    strategy: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None


class IndicatorCalculateRequest(BaseModel):
    indicator_list: List[Dict[str, Any]]


class IndicatorCalculateResponse(BaseModel):
    columns_added: List[str]
    total_indicators: int
    shape: List[int]
    sample: List[Dict[str, Any]]


class AvailableIndicatorsResponse(BaseModel):
    indicators: List[str]
    count: int
