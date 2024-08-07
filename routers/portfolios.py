from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from typing import List
from ..database import get_db
from ..models import User
from ..schemas import Stock, StockCreate
from ..crud import get_stocks, create_stock, get_stock, update_stock, delete_stock
from ..deps import db_dependency, user_dependency


router = APIRouter(
    prefix='/portfolios',
    tags=['portfolios']
)

@router.post("/stocks/", response_model=Stock)
def create_stock(stock: StockCreate, db: db_dependency, current_user: user_dependency):
    return create_stock(db=db, stock=stock, user_id=current_user['id'])

@router.get("/stocks/", response_model=List[Stock])
def read_stocks(db: db_dependency, current_user: user_dependency, skip: int = 0, limit: int = 10):
    stocks = get_stocks(db, user_id=current_user['id'], skip=skip, limit=limit)
    return stocks

@router.get("/stocks/{stock_id}", response_model=Stock)
def read_stock(stock_id: int, db: db_dependency, current_user: user_dependency):
    db_stock = get_stock(db, stock_id=stock_id, user_id=current_user['id'])
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return db_stock

@router.put("/stocks/{stock_id}", response_model=Stock)
def update_stock(stock_id: int, stock: StockCreate, db: db_dependency, current_user: user_dependency):
    db_stock = get_stock(db, stock_id=stock_id, user_id=current_user['id'])
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return update_stock(db=db, stock_id=stock_id, stock=stock)

@router.delete("/stocks/{stock_id}", response_model=Stock)
def remove_stock(stock_id: int, db: db_dependency, current_user: user_dependency):
    db_stock = get_stock(db, stock_id=stock_id, user_id=current_user['id'])
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return delete_stock(db=db, stock_id=stock_id)
