from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TransactionOut, UploadResponse
from app.services.transactions import get_transactions, parse_transactions_csv, save_transactions

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_transactions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed")

    try:
        df = parse_transactions_csv(file.file.read())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    inserted = save_transactions(db, df)
    return UploadResponse(inserted=inserted)


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    category: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_transactions(db, category, limit)
