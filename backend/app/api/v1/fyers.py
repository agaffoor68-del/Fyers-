from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.fyers_service import FyersService

router = APIRouter()
fyers_service = FyersService()


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: int
    order_type: str = "MARKET"
    price: float = 0
    stop_price: float = 0
    validity: str = "DAY"


class CandlesRequest(BaseModel):
    symbol: str = "NSE:SBIN-EQ"
    resolution: str = "5"
    days: int = 15


@router.get("/profile")
def get_profile():
    return fyers_service.get_profile()


@router.get("/quotes")
def get_quotes(symbols: str):
    """Comma-separated symbols"""
    symbol_list = [s.strip() for s in symbols.split(",")]
    return fyers_service.get_quotes(symbol_list)


@router.get("/candles")
def get_candles(symbol: str = "NSE:SBIN-EQ", resolution: str = "5", days: int = 15):
    return fyers_service.fetch_candles(symbol=symbol, resolution=resolution, days=days)


@router.post("/candles")
def get_candles_post(request: CandlesRequest):
    return fyers_service.fetch_candles(
        symbol=request.symbol,
        resolution=request.resolution,
        days=request.days
    )


@router.post("/orders")
def place_order(request: PlaceOrderRequest):
    result = fyers_service.place_order(
        symbol=request.symbol,
        side=request.side,
        quantity=request.quantity,
        order_type=request.order_type,
        price=request.price,
        stop_price=request.stop_price,
        validity=request.validity
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/orders")
def get_orderbook():
    return fyers_service.get_orderbook()


@router.get("/positions")
def get_positions():
    return fyers_service.get_positions()


@router.get("/funds")
def get_funds():
    return fyers_service.get_funds()
