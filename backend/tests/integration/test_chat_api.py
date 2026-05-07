"""Integration tests for POST /chat."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from prelegal import llm
from prelegal.config import Settings
from prelegal.main import create_app
from prelegal.models import ChatMessage, ChatResponse, PartialNdaFormValues


@pytest.fixture()
def chat_client(settings: Settings) -> TestClient:
    """A client whose backend has an OpenRouter key configured."""
    return TestClient(create_app(replace(settings, openrouter_api_key="test-key")))


@pytest.fixture()
def stub_assistant(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[dict]]:
    """Replace llm.chat_assist with a recorder that returns a fixed reply."""
    calls: list[dict] = []

    def fake(
        messages: list[ChatMessage],
        current_values: PartialNdaFormValues,
        api_key: str,
    ) -> ChatResponse:
        calls.append(
            {
                "messages": messages,
                "current_values": current_values,
                "api_key": api_key,
            }
        )
        return ChatResponse(
            assistant_message="Got it. What is the agreement title?",
            extracted_values=PartialNdaFormValues(governing_law="Delaware"),
        )

    monkeypatch.setattr(llm, "chat_assist", fake)
    yield calls


def test_chat_returns_503_when_api_key_unset(client: TestClient) -> None:
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "Hi"}], "currentValues": {}},
    )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"].lower()


def test_chat_returns_response_when_configured(
    chat_client: TestClient, stub_assistant: list[dict]
) -> None:
    response = chat_client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "Use Delaware law"}],
            "currentValues": {"title": "Draft"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["assistantMessage"].startswith("Got it")
    assert body["extractedValues"]["governingLaw"] == "Delaware"

    assert len(stub_assistant) == 1
    call = stub_assistant[0]
    assert call["api_key"] == "test-key"
    assert call["messages"][0].content == "Use Delaware law"
    assert call["current_values"].title == "Draft"


def test_chat_rejects_malformed_body(chat_client: TestClient) -> None:
    response = chat_client.post(
        "/chat",
        json={"messages": [{"role": "system", "content": "x"}], "currentValues": {}},
    )
    assert response.status_code == 422


def test_chat_returns_502_when_llm_raises_api_error(
    chat_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    import litellm

    def boom(*_args: object, **_kwargs: object) -> ChatResponse:
        raise litellm.APIError(
            status_code=500, message="upstream error", llm_provider="openrouter", model="x"
        )

    monkeypatch.setattr(llm, "chat_assist", boom)
    response = chat_client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "Hi"}], "currentValues": {}},
    )
    assert response.status_code == 502
    assert "unavailable" in response.json()["detail"].lower()


def test_chat_returns_502_when_llm_returns_malformed_json(
    chat_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the LLM returns a payload that fails ChatResponse validation, surface as 502."""
    from pydantic import ValidationError

    def boom(*_args: object, **_kwargs: object) -> ChatResponse:
        raise ValidationError.from_exception_data("ChatResponse", [])

    monkeypatch.setattr(llm, "chat_assist", boom)
    response = chat_client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "Hi"}], "currentValues": {}},
    )
    assert response.status_code == 502
