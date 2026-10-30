from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from app.db.session import get_db
from app.grok_ai.agent import GrokAgent
from app.db.models.models import AIConversation, AILearningLog
from app.grok_ai.strategy_builder import StrategyBuilder
from app.core.indicator_engine import IndicatorEngine

router = APIRouter()
grok_agent = GrokAgent()
strategy_builder = StrategyBuilder()
indicator_engine = IndicatorEngine()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class OptimizeRequest(BaseModel):
    market_data: dict = {}


class StrategyGenerateRequest(BaseModel):
    user_request: str
    symbol: str = "NSE:SBIN-EQ"
    days: int = 30
    resolution: str = "5"


class IndicatorCalculateRequest(BaseModel):
    indicator_list: List[Dict[str, Any]]


@router.post("/chat")
def chat_with_grok(request: ChatRequest, db: Session = Depends(get_db)):
    response = grok_agent.chat(db, request.message, request.session_id)

    user_msg = AIConversation(
        role="user", message=request.message, session_id=request.session_id
    )
    ai_msg = AIConversation(
        role="assistant", message=response, session_id=request.session_id
    )
    db.add(user_msg)
    db.add(ai_msg)
    db.commit()

    return {"response": response, "session_id": request.session_id}


@router.post("/auto-optimize")
def auto_optimize(request: OptimizeRequest, db: Session = Depends(get_db)):
    optimization = grok_agent.auto_optimize(db)
    return optimization


@router.post("/auto-optimize/multi-indicator")
def auto_optimize_multi_indicator(
    request: OptimizeRequest, db: Session = Depends(get_db)
):
    """Run multi-indicator auto-optimization using Grok + pandas_ta"""
    optimization = grok_agent.auto_optimize(db)
    return {
        **optimization,
        "indicator_toolkit": indicator_engine.list_available_indicators()[:50],
        "total_indicators_available": len(
            indicator_engine.list_available_indicators()
        ),
    }


@router.post("/generate-strategy")
def generate_strategy(
    request: StrategyGenerateRequest, db: Session = Depends(get_db)
):
    """Generate a strategy from Grok with full indicator toolkit"""
    result = grok_agent.generate_strategy(
        db, user_request=request.user_request
    )
    return result


@router.post("/calculate-indicators")
def calculate_indicators(
    request: IndicatorCalculateRequest, db: Session = Depends(get_db)
):
    """Calculate indicators on sample data (for testing)"""
    import pandas as pd
    import numpy as np

    # Generate sample data
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2024-01-01", periods=n, freq="5min")
    price = 1000 * np.exp(np.cumsum(np.random.randn(n) * 0.001))

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

    result_df = indicator_engine.calculate_indicators(df, request.indicator_list)

    return {
        "columns_added": [
            c for c in result_df.columns if c not in df.columns
        ],
        "total_indicators": len(request.indicator_list),
        "shape": result_df.shape,
        "sample": result_df.tail(5).to_dict(orient="records"),
    }


@router.get("/indicators/available")
def get_available_indicators():
    """List all available pandas_ta indicators"""
    return {
        "indicators": indicator_engine.list_available_indicators(),
        "count": len(indicator_engine.list_available_indicators()),
    }


@router.get("/memory")
def get_grok_memory(db: Session = Depends(get_db)):
    failures = db.query(AILearningLog).order_by(AILearningLog.timestamp.desc()).all()
    return {
        "failures": [
            {
                "id": f.id,
                "strategy_used": f.strategy_used,
                "reason_failed": f.reason_failed,
                "mistake_context": f.mistake_context,
                "lesson_learned": f.lesson_learned,
                "timestamp": f.timestamp.isoformat() if f.timestamp else None,
            }
            for f in failures
        ],
        "count": len(failures),
    }
