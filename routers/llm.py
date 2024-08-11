import openai

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..deps import db_dependency, user_dependency
from ..models import Stock
import os

router = APIRouter()

router = APIRouter(
    prefix='/llm',
    tags=['llm']
)

OPEN_API_KEY = os.getenv("OPEN_API_KEY")

openai.api_key = OPEN_API_KEY
@router.post("/llm/query/")
def llm_query(query: str, db: db_dependency, user: user_dependency):
    user_id = user['id']
    user_stocks = db.query(Stock).filter(Stock.user_id == user_id).all()

    # Format the stock data for GPT
    stocks_info = "\n".join([f"{stock.name} ({stock.symbol}): {stock.purchase_price} shares at ${stock.purchase_price} each" for stock in user_stocks])

    # Construct the prompt for GPT
    prompt = f"User's stock portfolio:\n{stocks_info}\n\n{query}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can also use "gpt-4" if you have access to it
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150
        )
        return {"result": response.choices[0].message['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))