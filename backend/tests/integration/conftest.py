from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from prelegal.config import Settings
from prelegal.main import create_app


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    """Base Settings pointing at the real templates dir and a per-test SQLite file."""
    repo_root = Path(__file__).resolve().parents[3]
    return Settings(
        database_path=tmp_path / "test.db",
        templates_dir=repo_root / "templates",
        catalog_path=repo_root / "catalog.json",
        cors_origins=("http://localhost:3000",),
    )


@pytest.fixture()
def client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings))


@pytest.fixture()
def sample_payload() -> dict:
    return {
        "title": "ACME × Globex Mutual NDA",
        "purpose": "Evaluate a potential commercial relationship.",
        "effectiveDate": "2026-05-06",
        "mndaTerm": {"type": "expires", "years": 2},
        "termOfConfidentiality": {"type": "perpetuity"},
        "governingLaw": "Delaware",
        "jurisdiction": "New Castle County, Delaware",
        "modifications": "",
        "parties": [
            {
                "printName": "Alice Example",
                "title": "CEO",
                "company": "ACME Inc.",
                "noticeAddress": "1 ACME Way",
                "signedDate": "",
            },
            {
                "printName": "Bob Sample",
                "title": "CTO",
                "company": "Globex LLC",
                "noticeAddress": "2 Globex Ave",
                "signedDate": "",
            },
        ],
    }
