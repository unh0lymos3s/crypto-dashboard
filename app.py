from pydantic import  BaseModel, field_validator
from fastapi import FastAPI, HTTPException


app = FastAPI()
quotes: dict[str, float] = {}

class quote(BaseModel):
    symbol: str
    price: float

    @field_validator("symbol", mode="before")
    def check_symbol(cls,v):
        if not v.isupper():
            raise ValueError("Symbol must be uppercase")
        return v
    @field_validator("price", mode="before")
    def check_price(cls,v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

@app.post("/quote/")
def post_quotes(quote: quote):
    quotes[quote.symbol] = quote.price
    return {
        "status": "saved",
        "symbol": quote.symbol,
        "price": quote.price
    }

@app.get("/quote/{symbol}")
def get_quotes(symbol: str):
    if symbol not in quotes:
        raise HTTPException(status_code=404, detail="Symbol not found")
    else:
        return {
        "symbol": symbol,
        "price": quotes[symbol]
        }

