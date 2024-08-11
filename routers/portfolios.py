from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

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

