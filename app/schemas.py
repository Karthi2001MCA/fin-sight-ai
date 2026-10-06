import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    inserted: int


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime.date
    description: str
    category: str
    amount: Decimal
    merchant: str
    transaction_type: str
