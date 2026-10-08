from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AnalyticsSummary, AnomalyOut
from app.services.analytics import get_summary
from app.services.anomaly import detect_anomalies

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db)):
    return get_summary(db)


@router.get("/anomalies", response_model=list[AnomalyOut])
def anomalies(db: Session = Depends(get_db)):
    return detect_anomalies(db)
