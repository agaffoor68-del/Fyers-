from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models.models import TradeLog, Strategy, PaperTrade
from app.schemas.schemas import (
    TradeLogOut, TradeLogCreate,
    StrategyOut, StrategyCreate,
    PaperTradeOut, PaperTradeCreate,
    AILearningLogOut
)
from app.services.paper_trade_service import PaperTradeService
from app.db.models.models import AILearningLog

router = APIRouter()


# TradeLog endpoints
@router.post("/tradelogs", response_model=TradeLogOut)
def create_tradelog(tradelog: TradeLogCreate, db: Session = Depends(get_db)):
    db_tradelog = TradeLog(**tradelog.model_dump())
    db.add(db_tradelog)
    db.commit()
    db.refresh(db_tradelog)
    return db_tradelog


@router.get("/tradelogs", response_model=List[TradeLogOut])
def get_tradelogs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(TradeLog).offset(skip).limit(limit).all()


@router.get("/tradelogs/{trad_id}", response_model=TradeLogOut)
def get_tradelog(trad_id: int, db: Session = Depends(get_db)):
    tradelog = db.query(TradeLog).filter(TradeLog.id == trad_id).first()
    if not tradelog:
        raise HTTPException(status_code=404, detail="TradeLog not found")
    return tradelog


# Strategy endpoints
@router.post("/strategies", response_model=StrategyOut)
def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    db_strategy = Strategy(**strategy.model_dump())
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.get("/strategies", response_model=List[StrategyOut])
def get_strategies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Strategy).offset(skip).limit(limit).all()


@router.get("/strategies/{strategy_id}", response_model=StrategyOut)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.put("/strategies/{strategy_id}", response_model=StrategyOut)
def update_strategy(strategy_id: int, strategy_update: StrategyCreate, db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    for key, value in strategy_update.model_dump(exclude_unset=True).items():
        setattr(strategy, key, value)
    db.commit()
    db.refresh(strategy)
    return strategy


@router.delete("/strategies/{strategy_id}")
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    db.delete(strategy)
    db.commit()
    return {"message": "Strategy deleted"}


# PaperTrade endpoints
@router.post("/paper-trades", response_model=PaperTradeOut)
def create_paper_trade(trade: PaperTradeCreate, db: Session = Depends(get_db)):
    service = PaperTradeService(db)
    paper_trade = service.execute_paper_trade(
        symbol=trade.symbol,
        side=trade.side,
        quantity=trade.quantity,
        entry_price=trade.entry_price,
        stop_loss=trade.stop_loss,
        take_profit=trade.take_profit,
        strategy_id=trade.strategy_id
    )
    return paper_trade


@router.get("/paper-trades", response_model=List[PaperTradeOut])
def get_paper_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(PaperTrade).offset(skip).limit(limit).all()


@router.get("/paper-trades/{trade_id}", response_model=PaperTradeOut)
def get_paper_trade(trade_id: int, db: Session = Depends(get_db)):
    trade = db.query(PaperTrade).filter(PaperTrade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Paper trade not found")
    return trade


@router.post("/paper-trades/{trade_id}/check-sl-tp")
def check_sl_tp(trade_id: int, current_price: float, db: Session = Depends(get_db)):
    trade = db.query(PaperTrade).filter(PaperTrade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Paper trade not found")
    
    service = PaperTradeService(db)
    result = service.check_stop_loss_take_profit(trade, current_price)
    return result


# AI Learning Log endpoints
@router.get("/ai-learning-log", response_model=List[AILearningLogOut])
def get_ai_learning_log(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AILearningLog).order_by(AILearningLog.timestamp.desc()).offset(skip).limit(limit).all()


@router.get("/ai-learning-log/{log_id}", response_model=AILearningLogOut)
def get_ai_learning_log_entry(log_id: int, db: Session = Depends(get_db)):
    log = db.query(AILearningLog).filter(AILearningLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="AI Learning Log entry not found")
    return log


@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_trades = db.query(TradeLog).count()
    total_paper_trades = db.query(PaperTrade).count()
    active_strategies = db.query(Strategy).filter(Strategy.is_active == True).count()
    total_failures = db.query(AILearningLog).count()
    
    winning_trades = db.query(TradeLog).filter(TradeLog.pnl > 0).count()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    return {
        "total_trades": total_trades,
        "total_paper_trades": total_paper_trades,
        "active_strategies": active_strategies,
        "total_ai_failures": total_failures,
        "win_rate": round(win_rate, 2)
    }
