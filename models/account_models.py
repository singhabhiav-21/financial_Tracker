from pydantic import BaseModel
from typing import Optional


class AccountCreate(BaseModel):
    name: str
    type: str
    balance: float
    currency: str = "USD"
    platform_name: Optional[str] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    accountType: Optional[str] = None
    balance: Optional[float] = None
    currency: Optional[str] = None
    platform_name: Optional[str] = None


class AccountDelete(BaseModel):
    password: str


class AddMoney(BaseModel):
    amount: float


class MoneyTransfer(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float