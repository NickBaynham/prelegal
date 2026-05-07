from pathlib import Path

import pytest

from prelegal import repo
from prelegal.models import NdaFormValues


def test_create_document_returns_first_version(
    db_path: Path, sample_values: NdaFormValues
) -> None:
    document_id, version_id, version_number = repo.create_document(
        db_path, sample_values, "rendered markdown"
    )
    assert document_id and version_id
    assert version_number == 1

    document = repo.get_document(db_path, document_id)
    assert document is not None
    assert document.title == "Sample NDA"

    latest = repo.get_latest_version(db_path, document_id)
    assert latest is not None
    assert latest.version_number == 1
    assert latest.rendered_markdown == "rendered markdown"
    assert latest.data.purpose == "Evaluate partnership."


def test_add_version_increments_and_updates_title(
    db_path: Path, sample_values: NdaFormValues
) -> None:
    document_id, _, _ = repo.create_document(db_path, sample_values, "v1")

    updated = sample_values.model_copy(update={"title": "Sample NDA — v2"})
    version_id, version_number = repo.add_version(db_path, document_id, updated, "v2")

    assert version_number == 2
    assert version_id

    document = repo.get_document(db_path, document_id)
    assert document is not None
    assert document.title == "Sample NDA — v2"

    versions = repo.list_versions(db_path, document_id)
    assert [v.version_number for v in versions] == [2, 1]


def test_add_version_for_missing_document_raises(
    db_path: Path, sample_values: NdaFormValues
) -> None:
    with pytest.raises(repo.DocumentNotFound):
        repo.add_version(db_path, "nonexistent-id", sample_values, "x")


def test_list_documents_orders_by_updated_at_desc(
    db_path: Path, sample_values: NdaFormValues
) -> None:
    first_id, _, _ = repo.create_document(db_path, sample_values, "a")
    second_values = sample_values.model_copy(update={"title": "Second NDA"})
    second_id, _, _ = repo.create_document(db_path, second_values, "b")

    summaries = repo.list_documents(db_path)
    assert [s.id for s in summaries] == [second_id, first_id]
    assert summaries[0].latest_version_number == 1
    assert summaries[1].latest_version_number == 1


def test_list_documents_returns_only_latest_version_per_document(
    db_path: Path, sample_values: NdaFormValues
) -> None:
    document_id, _, _ = repo.create_document(db_path, sample_values, "v1")
    repo.add_version(db_path, document_id, sample_values, "v2")
    repo.add_version(db_path, document_id, sample_values, "v3")

    summaries = repo.list_documents(db_path)
    assert len(summaries) == 1
    assert summaries[0].latest_version_number == 3


def test_get_version_returns_specific_version(
    db_path: Path, sample_values: NdaFormValues
) -> None:
    document_id, first_version_id, _ = repo.create_document(db_path, sample_values, "v1")
    second_version_id, _ = repo.add_version(db_path, document_id, sample_values, "v2")

    first = repo.get_version(db_path, document_id, first_version_id)
    assert first is not None
    assert first.rendered_markdown == "v1"

    second = repo.get_version(db_path, document_id, second_version_id)
    assert second is not None
    assert second.rendered_markdown == "v2"


def test_get_version_returns_none_when_missing(
    db_path: Path, sample_values: NdaFormValues
) -> None:
    document_id, _, _ = repo.create_document(db_path, sample_values, "v1")
    assert repo.get_version(db_path, document_id, "no-such-version") is None


def test_get_document_detail_combines_document_and_latest_version(
    db_path: Path, sample_values: NdaFormValues
) -> None:
    document_id, _, _ = repo.create_document(db_path, sample_values, "v1")
    repo.add_version(db_path, document_id, sample_values, "v2")

    detail = repo.get_document_detail(db_path, document_id)
    assert detail is not None
    assert detail.document.id == document_id
    assert detail.latest_version.version_number == 2
    assert detail.latest_version.rendered_markdown == "v2"


def test_concurrent_add_version_assigns_unique_numbers(
    db_path: Path, sample_values: NdaFormValues
) -> None:
    """Two threads writing simultaneously must not collide on version_number."""
    import threading

    document_id, _, _ = repo.create_document(db_path, sample_values, "v1")

    results: list[tuple[str, int]] = []
    errors: list[Exception] = []

    def worker() -> None:
        try:
            results.append(repo.add_version(db_path, document_id, sample_values, "x"))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, errors
    numbers = sorted(n for _, n in results)
    assert numbers == [2, 3, 4, 5, 6]
