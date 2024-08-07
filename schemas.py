from pydantic import BaseModel
from typing import List

class StockBase(BaseModel):
    name: str
    symbol: str
    quantity: float
    purchase_price: float
    purchase_date: str

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    stocks: List[Stock] = []

    class Config:
        orm_mode = True
