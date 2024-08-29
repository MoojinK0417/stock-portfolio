from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
import yfinance as yf
import numpy as np

from typing import List
from ..database import get_db
from ..models import Stock as StockModel  # SQLAlchemy model
from ..models import User # SQLAlchemy model
from ..schemas import StockCreate, Stock as StockSchema  # Pydantic models
from ..deps import db_dependency, user_dependency


router = APIRouter(
    prefix='/portfolios',
    tags=['portfolios']
)

@router.get("/{user_id}", response_model=List[StockSchema])
def get_stocks(user_id: int, db: db_dependency, user: user_dependency):
    stocks = db.query(StockModel).filter(StockModel.user_id == user_id).all() 
    return stocks 

@router.get("/stocks/{user_id}/{stock_id}", response_model=StockSchema)
def get_stock(user_id: int, stock_id: int, db: db_dependency, current_user: user_dependency):
    db_stock = db.query(StockModel).filter(StockModel.id == stock_id, StockModel.user_id == user_id).first() # Query using SQLAlchemy model
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock 


@router.put("/stocks/{user_id}/{stock_id}", response_model=StockSchema)
def update_stock(user_id: int, stock_id: int, stock: StockCreate, db: db_dependency, current_user: user_dependency):
    db_stock = db.query(StockModel).filter(StockModel.id == stock_id, StockModel.user_id == user_id).first()
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    db_stock = db.query(StockModel).filter(StockModel.id == stock_id).first()
    db_stock.name = stock.name
    db_stock.symbol = stock.symbol
    db_stock.quantity = stock.quantity
    db_stock.purchase_price = stock.purchase_price
    db_stock.purchase_date = stock.purchase_date
    db.commit()
    db.refresh(db_stock)
    return db_stock 


@router.delete("/stocks/{user_id}/{stock_id}", response_model=StockSchema)
def sell_stock(user_id: int, stock_id: int, db: db_dependency, current_user: user_dependency):
    # Fetch the stock to be sold
    db_stock = db.query(StockModel).filter(StockModel.id == stock_id, StockModel.user_id == user_id).first()
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")

    # Fetch the current user
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.balance is None:
        db_user.balance = 0.0

    # Fetch the current price using yfinance
    ticker = yf.Ticker(db_stock.symbol)
    history = ticker.history(period='1d', interval='15m')
    
    if history.empty:
        raise HTTPException(status_code=404, detail="Could not retrieve the current price for this stock.")
    
    latest_price = float(history.iloc[-1]['Close']) 

    # Calculate the total value of the stock being sold
    total_value = float(latest_price * db_stock.quantity)

    # Add the total value to the user's balance
    db_user.balance += total_value

    # Delete the stock
    db.delete(db_stock)
    db.commit()
    
    # Return the sold stock information
    return db_stock

@router.get("/stocks/{user_id}/current_prices/", response_model=List[dict])
def get_current_prices(user_id: int, db: db_dependency, current_user: user_dependency):
    # Fetch all stocks for the user
    stocks = db.query(StockModel).filter(StockModel.user_id == user_id).all()
    if not stocks:
        raise HTTPException(status_code=404, detail="No stocks found for this user.")
    
    # Fetch current prices using yfinance
    prices = []
    for stock in stocks:
        ticker = yf.Ticker(stock.symbol)
        history = ticker.history(period='1d', interval='15m')
        
        if history.empty:
            latest_price = None
            # You might want to log or handle this scenario where no data is returned
        else:
            latest_price = history.iloc[-1]['Close']
      # Calculate initial value and current total value
        initial_value = stock.purchase_price * stock.quantity
        current_total_value = (latest_price * stock.quantity) if latest_price is not None else None

        # Calculate profit
        profit = (current_total_value - initial_value) if current_total_value is not None else "N/A"

        prices.append({
            "name": stock.name,
            "symbol": stock.symbol,
            "current_price": f"{latest_price:.2f}" if latest_price is not None else "N/A",
            "average_price": f"{stock.purchase_price:.2f}" if latest_price is not None else "N/A",
            "quantity": stock.quantity,
            "total_value": f"{current_total_value:.2f}" if current_total_value is not None else "N/A",
            "profit": f"{profit:.2f}" if profit != "N/A" else "N/A"
        })
    return prices

@router.post("/stocks/search/", response_model=StockSchema)
def search_and_add_stock(symbol: str, quantity: int, db: db_dependency, user: user_dependency):
    # Search for stock data using yfinance
    ticker = yf.Ticker(symbol)
    
    # Retrieve stock information
    stock_info = ticker.info
    
    if not stock_info:
        raise HTTPException(status_code=404, detail="Stock symbol not found.")

    # Fetch the latest price and ensure it's a regular float
    history = ticker.history(period='1d', interval='15m')
    if history.empty:
        raise HTTPException(status_code=404, detail="No price data available for this symbol.")

    purchase_price = float(history.iloc[-1]['Close'])

    # Check if the user already owns this stock
    existing_stock = db.query(StockModel).filter(StockModel.user_id == user.get('id'), StockModel.symbol == symbol).first()

    if existing_stock:
        # Calculate the new average purchase price and update quantity
        total_quantity = existing_stock.quantity + quantity
        total_value = (existing_stock.purchase_price * existing_stock.quantity) + (purchase_price * quantity)
        average_price = total_value / total_quantity

        # Update the existing stock with the new quantity and average price
        existing_stock.quantity = total_quantity
        existing_stock.purchase_price = average_price
        existing_stock.purchase_date = history.index[-1].date()  # Update purchase date to the latest purchase
        db.commit()
        db.refresh(existing_stock)
        return existing_stock
    else:
        # If the stock doesn't exist, create a new record
        stock_data = {
            "name": stock_info.get("shortName", symbol),
            "symbol": symbol,
            "quantity": quantity,
            "purchase_price": purchase_price,
            "initial_value": purchase_price * quantity,
            "purchase_date": history.index[-1].date()
        }

        db_stock = StockModel(**stock_data, user_id=user.get('id'))
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
        return db_stock