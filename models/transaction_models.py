from pydantic import BaseModel
from typing import Optional
from datetime import date


class TransactionCreate(BaseModel):
    category_id: int
    name: str
    amount: float
    description: Optional[str] = None
    transaction_date: Optional[date] = None
    balance: Optional[float] = None


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None