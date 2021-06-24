from datetime import datetime

from pydantic import BaseModel


class BitcoinIn(BaseModel):
    price: float
    updatedAt: datetime
