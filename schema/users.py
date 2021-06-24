from datetime import datetime
from enum import Enum
from typing import List, Optional, Set

from pydantic import BaseModel, EmailStr


class UsdAction(Enum):
    withdraw = "withdraw"
    deposit = "deposit"


class BitcoinAction(Enum):
    buy = "buy"
    sell = "sell"


class UserIn(BaseModel):
    username: str
    email: EmailStr
    name: str


class UserOut(UserIn):
    id: str
    bitcoinAmount: float
    usdBalance: float
    createdAt: datetime
    updatedAt: datetime


class UserInDb(UserIn):
    id: str
    bitcoinAmount: float = 0.00
    usdBalance: float = 0.00
    createdAt: datetime
    updatedAt: datetime = datetime.now()


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserUsdTransaction(BaseModel):
    action: UsdAction
    amount: float


class UserBitcoinTransaction(BaseModel):
    action: BitcoinAction
    amount: float


class UserBalance(BaseModel):
    total_balance: float
