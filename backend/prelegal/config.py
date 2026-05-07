"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_ROOT.parent


@dataclass(frozen=True)
class Settings:
    database_path: Path
    templates_dir: Path
    catalog_path: Path
    cors_origins: tuple[str, ...]
    openrouter_api_key: str | None = None


def load_settings() -> Settings:
    return Settings(
        database_path=Path(os.environ.get("DATABASE_PATH", _BACKEND_ROOT / "data" / "prelegal.db")),
        templates_dir=Path(os.environ.get("TEMPLATES_DIR", _REPO_ROOT / "templates")),
        catalog_path=Path(os.environ.get("CATALOG_PATH", _REPO_ROOT / "catalog.json")),
        cors_origins=tuple(
            origin.strip()
            for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
            if origin.strip()
        ),
        openrouter_api_key=os.environ.get("OPENROUTER_API_KEY") or None,
    )
