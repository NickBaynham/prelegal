"""Loader for the document catalog descriptor."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class CatalogDocument(BaseModel):
    name: str
    description: str
    file: str


class Catalog(BaseModel):
    source: str
    license: str
    documents: list[CatalogDocument]


@lru_cache(maxsize=4)
def load_catalog(path_str: str) -> Catalog:
    raw = json.loads(Path(path_str).read_text(encoding="utf8"))
    return Catalog.model_validate(raw)
