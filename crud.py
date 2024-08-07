from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from .models import User, Stock
from .schemas import UserCreate, StockCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_stock(db: Session, stock: StockCreate, user_id: int):
    db_stock = Stock(**stock.dict(), user_id=user_id)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def get_stocks(db: Session, user_id: int):
    return db.query(Stock).filter(Stock.user_id == user_id).all()

# def get_stocks(db: Session, user_id: int, skip: int = 0, limit: int = 10):
#     return db.query(Stock).filter(Stock.user_id == user_id).offset(skip).limit(limit).all()

def get_stock(db: Session, stock_id: int, user_id: int):
    return db.query(Stock).filter(Stock.id == stock_id, Stock.user_id == user_id).first()

def update_stock(db: Session, stock_id: int, stock: StockCreate):
    db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
    db_stock.name = stock.name
    db_stock.symbol = stock.symbol
    db_stock.quantity = stock.quantity
    db_stock.purchase_price = stock.purchase_price
    db_stock.purchase_date = stock.purchase_date
    db.commit()
    db.refresh(db_stock)
    return db_stock

def delete_stock(db: Session, stock_id: int):
    db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
    db.delete(db_stock)
    db.commit()
    return db_stock