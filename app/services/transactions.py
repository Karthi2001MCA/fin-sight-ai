import io

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Transaction


REQUIRED_COLUMNS = {
    "date", "description", "category",
    "amount", "merchant", "transaction_type",
}


def parse_transactions_csv(content: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content))

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df.dropna(subset=list(REQUIRED_COLUMNS))
    if df.empty:
        raise ValueError("CSV contains no valid rows")

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d").dt.date
    df["amount"] = pd.to_numeric(df["amount"]).round(2)
    df["transaction_type"] = df["transaction_type"].str.strip().str.lower()

    if not df["transaction_type"].isin(["debit", "credit"]).all():
        raise ValueError("transaction_type must be 'debit' or 'credit'")

    return df


def save_transactions(db: Session, df: pd.DataFrame) -> int:
    records = df[list(REQUIRED_COLUMNS)].to_dict(orient="records")
    db.add_all([Transaction(**row) for row in records])
    db.commit()
    return len(records)


def get_transactions(db: Session, category: str | None = None, limit: int = 100):
    query = select(Transaction).order_by(Transaction.date.desc())
    if category:
        query = query.where(Transaction.category == category)
    return db.scalars(query.limit(limit)).all()
 