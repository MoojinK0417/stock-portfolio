from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
import yfinance as yf

from typing import List
from ..database import get_db
from ..models import Stock as StockModel  # SQLAlchemy model
from ..schemas import StockCreate, Stock as StockSchema  # Pydantic models
from ..deps import db_dependency, user_dependency


router = APIRouter(
    prefix='/stocks',
    tags=['stocks']
)

@router.get("/search/{symbol}", response_model=dict)
def get_current_price(symbol: str, user: user_dependency):

    ticker = yf.Ticker(symbol)
    history = ticker.history(period='1d', interval='5m')

    # Retrieve stock information
    stock_info = ticker.info
        
    if history.empty:
        return {"error": "No data available for this symbol."}

    # Prepare historical data for candlestick chart
    historical_data = []
    for index, row in history.iterrows():
        historical_data.append({
            "date": index.strftime('%Y-%m-%d %H:%M:%S'),
            "open": row['Open'],
            "high": row['High'],
            "low": row['Low'],
            "close": row['Close']
        })

    stock_data = {
        "name": stock_info.get("shortName", symbol),
        "symbol": symbol,
        "current_price": f"{history.iloc[-1]['Close']:.2f}",
        "history": historical_data
    }

    return stock_data
