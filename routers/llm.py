import openai

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import db_dependency, user_dependency
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
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=query,
            max_tokens=150
        )
        return response.choices[0].text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))