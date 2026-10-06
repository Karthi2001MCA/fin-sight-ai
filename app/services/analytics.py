from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Transaction

is_debit = Transaction.transaction_type == "debit"
total_amount = func.sum(Transaction.amount)


def _totals_by(db: Session, column, order, limit=None):
    query = (
        select(column.label("name"), total_amount.label("total"))
        .where(is_debit)
        .group_by("name")
        .order_by(order)
        .limit(limit)
    )
    return [{"name": name, "total": total} for name, total in db.execute(query)]


def get_summary(db: Session) -> dict:
    total, average, highest = db.execute(
        select(
            func.coalesce(total_amount, 0),
            func.coalesce(func.round(func.avg(Transaction.amount), 2), 0),
            func.coalesce(func.max(Transaction.amount), 0),
        ).where(is_debit)
    ).one()

    month = func.to_char(Transaction.date, "YYYY-MM")
    return {
        "total_spending": total,
        "average_transaction": average,
        "highest_transaction": highest,
        "by_category": _totals_by(db, Transaction.category, total_amount.desc()),
        "by_month": _totals_by(db, month, "name"),
        "top_merchants": _totals_by(db, Transaction.merchant, total_amount.desc(), 5),
    }
