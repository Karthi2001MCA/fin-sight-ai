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


class NameTotal(BaseModel):
    name: str
    total: Decimal


class AnalyticsSummary(BaseModel):
    total_spending: Decimal
    average_transaction: Decimal
    highest_transaction: Decimal
    by_category: list[NameTotal]
    by_month: list[NameTotal]
    top_merchants: list[NameTotal]
