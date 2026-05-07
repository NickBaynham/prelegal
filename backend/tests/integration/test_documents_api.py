from fastapi.testclient import TestClient


def test_create_document_returns_201_and_id(client: TestClient, sample_payload: dict) -> None:
    response = client.post("/documents", json=sample_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["latest_version_id"]
    assert body["latest_version_number"] == 1


def test_get_document_returns_detail_with_latest_version(
    client: TestClient, sample_payload: dict
) -> None:
    created = client.post("/documents", json=sample_payload).json()
    response = client.get(f"/documents/{created['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["document"]["id"] == created["id"]
    assert body["latest_version"]["version_number"] == 1
    assert "Mutual Non-Disclosure Agreement" in body["latest_version"]["rendered_markdown"]


def test_get_unknown_document_returns_404(client: TestClient) -> None:
    response = client.get("/documents/does-not-exist")
    assert response.status_code == 404


def test_list_documents_returns_summaries_newest_first(
    client: TestClient, sample_payload: dict
) -> None:
    first = client.post("/documents", json=sample_payload).json()
    second_payload = {**sample_payload, "title": "Second"}
    second = client.post("/documents", json=second_payload).json()

    response = client.get("/documents")
    assert response.status_code == 200
    summaries = response.json()
    assert [s["id"] for s in summaries] == [second["id"], first["id"]]


def test_create_version_increments_number(client: TestClient, sample_payload: dict) -> None:
    created = client.post("/documents", json=sample_payload).json()
    updated = {**sample_payload, "title": "Renamed"}
    response = client.post(f"/documents/{created['id']}/versions", json=updated)
    assert response.status_code == 201
    body = response.json()
    assert body["version_number"] == 2

    detail = client.get(f"/documents/{created['id']}").json()
    assert detail["document"]["title"] == "Renamed"
    assert detail["latest_version"]["version_number"] == 2


def test_create_version_for_missing_document_returns_404(
    client: TestClient, sample_payload: dict
) -> None:
    response = client.post("/documents/missing/versions", json=sample_payload)
    assert response.status_code == 404


def test_list_versions_returns_history_newest_first(
    client: TestClient, sample_payload: dict
) -> None:
    created = client.post("/documents", json=sample_payload).json()
    client.post(f"/documents/{created['id']}/versions", json=sample_payload)

    response = client.get(f"/documents/{created['id']}/versions")
    assert response.status_code == 200
    versions = response.json()
    assert [v["version_number"] for v in versions] == [2, 1]


def test_list_versions_for_missing_document_returns_404(client: TestClient) -> None:
    response = client.get("/documents/missing/versions")
    assert response.status_code == 404


def test_get_specific_version_returns_data(client: TestClient, sample_payload: dict) -> None:
    created = client.post("/documents", json=sample_payload).json()
    response = client.get(
        f"/documents/{created['id']}/versions/{created['latest_version_id']}"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["title"] == sample_payload["title"]


def test_get_unknown_version_returns_404(client: TestClient, sample_payload: dict) -> None:
    created = client.post("/documents", json=sample_payload).json()
    response = client.get(f"/documents/{created['id']}/versions/no-such-version")
    assert response.status_code == 404


def test_invalid_payload_returns_422(client: TestClient, sample_payload: dict) -> None:
    bad_payload = {**sample_payload, "effectiveDate": "not-a-date"}
    response = client.post("/documents", json=bad_payload)
    assert response.status_code == 422


def test_persistence_survives_app_recreation(tmp_path, sample_payload: dict) -> None:
    """Critical: data persists across backend restarts (acceptance criterion)."""
    from pathlib import Path

    from prelegal.config import Settings
    from prelegal.main import create_app

    repo_root = Path(__file__).resolve().parents[3]
    settings = Settings(
        database_path=tmp_path / "persist.db",
        templates_dir=repo_root / "templates",
        catalog_path=repo_root / "catalog.json",
        cors_origins=("http://localhost:3000",),
    )

    first_app = TestClient(create_app(settings))
    created = first_app.post("/documents", json=sample_payload).json()

    second_app = TestClient(create_app(settings))
    response = second_app.get(f"/documents/{created['id']}")
    assert response.status_code == 200
    assert response.json()["document"]["id"] == created["id"]
