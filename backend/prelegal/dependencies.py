"""FastAPI dependency providers.

Settings live on `app.state` so tests can override them by constructing the
app with a different `Settings` instance.
"""

from __future__ import annotations

from fastapi import Request

from .config import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings
