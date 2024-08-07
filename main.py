from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from .database import Base, engine
from .routers import portfolios, llm, auth
 

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/")
def health_check():
    return 'Health check complete'

app.include_router(auth.router)
# app.include_router(users.router)
app.include_router(portfolios.router)
# app.include_router(market.router)
app.include_router(llm.router)