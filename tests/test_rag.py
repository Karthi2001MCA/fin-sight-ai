from app.services import rag


def test_retrieves_relevant_chunk(tmp_path, monkeypatch):
    monkeypatch.setattr(rag, "INDEX_DIR", tmp_path / "index")
    with open("data/sample_invoice.txt", "rb") as f:
        chunks = rag.ingest_document("sample_invoice.txt", f.read())

    assert chunks > 0
    best = rag._load_index().similarity_search("When do I have to pay?", k=1)[0]
    assert "Payment is due within 15 days" in best.page_content
    assert best.metadata["source"] == "sample_invoice.txt"
