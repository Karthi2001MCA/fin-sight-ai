from fastapi import FastAPI

from app import models  # noqa: F401 - registers tables with Base
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinSight AI",
    description="Intelligent Financial Data Assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
