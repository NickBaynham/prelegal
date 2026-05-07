"""Chat endpoint for the AI-driven NDA assistant."""

from __future__ import annotations

import litellm
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from .. import llm
from ..config import Settings
from ..dependencies import get_settings
from ..models import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest, settings: Settings = Depends(get_settings)) -> ChatResponse:
    if not settings.openrouter_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI assistant is not configured.",
        )
    try:
        return llm.chat_assist(body.messages, body.current_values, settings.openrouter_api_key)
    except (litellm.APIError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI assistant is unavailable.",
        ) from exc
