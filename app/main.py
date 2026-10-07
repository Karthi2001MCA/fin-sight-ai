from fastapi import FastAPI

from app import models  # noqa: F401 - registers tables with Base
from app.database import Base, engine
from app.routes import analytics, chat, documents, transactions

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinSight AI",
    description="Intelligent Financial Data Assistant",
    version="0.1.0",
)

app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
