import os

os.environ["POSTGRES_DB"] = "finsight_test"
os.environ.setdefault("GOOGLE_API_KEY", "test-key-not-used")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Transaction  # noqa: E402

SAMPLE_CSV = "data/sample_transactions.csv"


@pytest.fixture(autouse=True)
def clean_database():
    db = SessionLocal()
    db.query(Transaction).delete()
    db.commit()
    db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def uploaded(client):
    with open(SAMPLE_CSV, "rb") as f:
        response = client.post("/transactions/upload", files={"file": ("sample.csv", f)})
    assert response.status_code == 201
    return response.json()
