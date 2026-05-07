from pathlib import Path

import pytest

from prelegal.db import init_db
from prelegal.models import NdaFormValues


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    init_db(path)
    return path


@pytest.fixture()
def sample_values() -> NdaFormValues:
    return NdaFormValues.model_validate(
        {
            "title": "Sample NDA",
            "purpose": "Evaluate partnership.",
            "effectiveDate": "2026-05-06",
            "mndaTerm": {"type": "expires", "years": 2},
            "termOfConfidentiality": {"type": "perpetuity"},
            "governingLaw": "Delaware",
            "jurisdiction": "Delaware",
            "modifications": "",
            "parties": [
                {
                    "printName": "Alice",
                    "title": "CEO",
                    "company": "ACME",
                    "noticeAddress": "1 Way",
                    "signedDate": "",
                },
                {
                    "printName": "Bob",
                    "title": "CTO",
                    "company": "Globex",
                    "noticeAddress": "2 Ave",
                    "signedDate": "",
                },
            ],
        }
    )
