"""Catalog endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..catalog import Catalog, load_catalog
from ..config import Settings
from ..dependencies import get_settings

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("", response_model=Catalog)
def get_catalog(settings: Settings = Depends(get_settings)) -> Catalog:
    return load_catalog(str(settings.catalog_path))
