import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Transaction

MIN_TRANSACTIONS = 5
CONTAMINATION = 0.1


def detect_anomalies(db: Session) -> list[dict]:
    txns = db.scalars(select(Transaction).where(Transaction.transaction_type == "debit")).all()
    if len(txns) < MIN_TRANSACTIONS:
        return []

    df = pd.DataFrame([
        {"id": t.id, "date": t.date, "description": t.description,
         "category": t.category, "merchant": t.merchant, "amount": float(t.amount)}
        for t in txns
    ])
    features = pd.DataFrame({
        "log_amount": np.log1p(df["amount"]),
        "day_of_week": pd.to_datetime(df["date"]).dt.dayofweek,
    })

    model = IsolationForest(contamination=CONTAMINATION, random_state=42).fit(features)
    df["anomaly_score"] = model.decision_function(features).round(3)
    flagged = df[model.predict(features) == -1]
    return flagged.sort_values("anomaly_score").to_dict(orient="records")
