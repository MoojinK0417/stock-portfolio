from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
import yfinance as yf

from typing import List
from ..database import get_db
from ..models import Stock as StockModel  # SQLAlchemy model
from ..schemas import StockCreate, Stock as StockSchema  # Pydantic models
from ..deps import db_dependency, user_dependency


router = APIRouter(
    prefix='/portfolios',
    tags=['portfolios']
)

@router.post("/", response_model=StockSchema, status_code=status.HTTP_201_CREATED)
def create_stock(stock: StockCreate, db: db_dependency, user: user_dependency):
    db_stock = StockModel(**stock.model_dump(), user_id=user.get('id')) 
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock 

@router.get("/", response_model=List[StockSchema])
def get_stocks(db: db_dependency, user: user_dependency):
    stocks = db.query(StockModel).filter(StockModel.user_id == user.get('id')).all() 
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
def delete_stock(user_id:int, stock_id: int, db: db_dependency, current_user: user_dependency):
    db_stock = db.query(StockModel).filter(StockModel.id == stock_id, StockModel.user_id == user_id).first()
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    db_stock = db.query(StockModel).filter(StockModel.id == stock_id).first()
    db.delete(db_stock)
    db.commit()  
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

        prices.append({
            "name": stock.name,
            "symbol": stock.symbol,
            "current_price": f"{latest_price:.2f}" if latest_price is not None else "N/A",
            "quantity": stock.quantity,
            "total_value": f"{(latest_price * stock.quantity):.2f}" if latest_price is not None else "N/A"
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

    purchase_price = float(history.iloc[-1]['Close'])  # Convert to regular float
    
    # Prepare stock data to fit into the StockModel
    stock_data = {
        "name": stock_info.get("shortName", symbol),
        "symbol": symbol,
        "quantity": quantity,
        "purchase_price": f"{purchase_price:.2f}",  # Use regular float here
        "purchase_date": history.index[-1].date()  # Get the most recent date
    }

    # Insert the stock data into the database
    db_stock = StockModel(**stock_data, user_id=user.get('id'))
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock
