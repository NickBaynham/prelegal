"""Document and version REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from .. import repo
from ..config import Settings
from ..dependencies import get_settings
from ..models import (
    CreateDocumentResponse,
    CreateVersionResponse,
    DocumentDetail,
    DocumentSummary,
    NdaFormValues,
    VersionRow,
)
from ..render import render_nda

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentSummary])
def list_documents(settings: Settings = Depends(get_settings)) -> list[DocumentSummary]:
    return repo.list_documents(settings.database_path)


@router.post(
    "",
    response_model=CreateDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    values: NdaFormValues,
    settings: Settings = Depends(get_settings),
) -> CreateDocumentResponse:
    rendered = render_nda(values, settings.templates_dir)
    document_id, version_id, version_number = repo.create_document(
        settings.database_path, values, rendered
    )
    return CreateDocumentResponse(
        id=document_id,
        latest_version_id=version_id,
        latest_version_number=version_number,
    )


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: str, settings: Settings = Depends(get_settings)
) -> DocumentDetail:
    detail = repo.get_document_detail(settings.database_path, document_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return detail


@router.get("/{document_id}/versions", response_model=list[VersionRow])
def list_versions(
    document_id: str, settings: Settings = Depends(get_settings)
) -> list[VersionRow]:
    if repo.get_document(settings.database_path, document_id) is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return repo.list_versions(settings.database_path, document_id)


@router.get("/{document_id}/versions/{version_id}", response_model=VersionRow)
def get_version(
    document_id: str,
    version_id: str,
    settings: Settings = Depends(get_settings),
) -> VersionRow:
    version = repo.get_version(settings.database_path, document_id, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.post(
    "/{document_id}/versions",
    response_model=CreateVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_version(
    document_id: str,
    values: NdaFormValues,
    settings: Settings = Depends(get_settings),
) -> CreateVersionResponse:
    rendered = render_nda(values, settings.templates_dir)
    try:
        version_id, version_number = repo.add_version(
            settings.database_path, document_id, values, rendered
        )
    except repo.DocumentNotFound as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    return CreateVersionResponse(version_id=version_id, version_number=version_number)
