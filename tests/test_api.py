def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_csv_inserts_rows(uploaded):
    assert uploaded == {"inserted": 12}


def test_upload_rejects_non_csv(client):
    response = client.post("/transactions/upload", files={"file": ("notes.txt", b"hello")})
    assert response.status_code == 400


def test_upload_rejects_missing_columns(client):
    response = client.post("/transactions/upload", files={"file": ("bad.csv", b"date,amount\n2026-09-01,100")})
    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]

def test_list_transactions_filters_by_category(client, uploaded):
    response = client.get("/transactions", params={"category": "Food"})
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_analytics_summary(client, uploaded):
    summary = client.get("/analytics/summary").json()
    assert summary["total_spending"] == "93670.50"
    assert summary["top_merchants"][0] == {"name": "Amazon", "total": "87200.00"}


def test_analytics_summary_empty_database(client):
    summary = client.get("/analytics/summary").json()
    assert summary["total_spending"] == "0"
    assert summary["by_category"] == []


def test_anomalies_flag_the_laptop(client, uploaded):
    flagged = client.get("/analytics/anomalies").json()
    assert [t["description"] for t in flagged] == ["Laptop purchase"]


def test_chat_blocks_unsafe_sql(client, uploaded, monkeypatch):
    monkeypatch.setattr("app.services.chat.generate_sql", lambda db, q: "DELETE FROM transactions")
    response = client.post("/chat", json={"question": "delete everything"})
    assert response.status_code == 400
    assert "blocked" in response.json()["detail"]
    assert len(client.get("/transactions").json()) == 12
