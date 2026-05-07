from fastapi.testclient import TestClient


def test_catalog_returns_documents_list(client: TestClient) -> None:
    response = client.get("/catalog")
    assert response.status_code == 200
    body = response.json()
    assert "documents" in body
    assert any(doc["file"] == "templates/Mutual-NDA.md" for doc in body["documents"])
    assert body["source"]
    assert body["license"]
