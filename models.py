from sqlalchemy import Column, Date, Float, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = 'users'  # Ensure table name matches the foreign key references
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    stocks = relationship('Stock', back_populates='owner')

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, index=True)
    symbol = Column(String, index=True)
    quantity = Column(Float)
    purchase_price = Column(Float)
    initial_value = Column(Float)
    purchase_date = Column(Date)
    owner = relationship("User", back_populates="stocks")