"""Tests for chat-related Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from prelegal.models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    NdaFormValues,
    PartialNdaFormValues,
    PartialParty,
    Party,
)


def test_partial_nda_accepts_empty_object() -> None:
    values = PartialNdaFormValues.model_validate({})
    assert values.title is None
    assert values.party1 is None


def test_partial_nda_accepts_subset_with_camelcase_aliases() -> None:
    values = PartialNdaFormValues.model_validate(
        {"title": "Draft", "effectiveDate": "2026-05-07", "governingLaw": "Delaware"}
    )
    assert values.title == "Draft"
    assert values.effective_date == "2026-05-07"
    assert values.governing_law == "Delaware"
    assert values.jurisdiction is None


def test_partial_nda_round_trips_via_alias_json() -> None:
    original = PartialNdaFormValues.model_validate(
        {
            "title": "Draft",
            "mndaTerm": {"type": "expires", "years": 2},
            "party1": {"company": "ACME"},
        }
    )
    restored = PartialNdaFormValues.model_validate_json(
        original.model_dump_json(by_alias=True, exclude_none=True)
    )
    assert restored == original


def test_partial_nda_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        PartialNdaFormValues.model_validate({"surprise": "hello"})


def test_partial_nda_mnda_term_must_be_complete_when_present() -> None:
    """A discriminated union is either fully present or absent — no half-filled term."""
    with pytest.raises(ValidationError):
        PartialNdaFormValues.model_validate({"mndaTerm": {"type": "expires"}})


def test_partial_party_accepts_single_field() -> None:
    party = PartialParty.model_validate({"company": "ACME"})
    assert party.company == "ACME"
    assert party.print_name is None


def test_chat_request_deserialises_camelcase_payload() -> None:
    body = ChatRequest.model_validate(
        {
            "messages": [{"role": "user", "content": "Hi"}],
            "currentValues": {"title": "Draft"},
        }
    )
    assert body.messages[0].content == "Hi"
    assert body.current_values.title == "Draft"


def test_chat_request_rejects_invalid_role() -> None:
    with pytest.raises(ValidationError):
        ChatRequest.model_validate(
            {
                "messages": [{"role": "system", "content": "Hi"}],
                "currentValues": {},
            }
        )


def test_chat_response_serialises_alias_keys() -> None:
    response = ChatResponse(
        assistant_message="Got it.",
        extracted_values=PartialNdaFormValues(title="Draft"),
    )
    payload = response.model_dump(by_alias=True)
    assert "assistantMessage" in payload
    assert "extractedValues" in payload
    assert payload["extractedValues"]["title"] == "Draft"


def test_chat_message_round_trips() -> None:
    msg = ChatMessage(role="assistant", content="Hello.")
    restored = ChatMessage.model_validate_json(msg.model_dump_json())
    assert restored == msg


def test_chat_response_rejects_unknown_keys() -> None:
    """The LLM is held to its schema; drift surfaces as a validation error, not silent passthrough."""
    with pytest.raises(ValidationError):
        ChatResponse.model_validate(
            {"assistantMessage": "Hi", "extractedValues": {}, "stray": True}
        )


def test_partial_party_field_names_track_party() -> None:
    """If a field is added to Party, PartialParty must add it too — caught here."""
    assert set(PartialParty.model_fields.keys()) == set(Party.model_fields.keys())


def test_partial_nda_field_names_track_nda_form_values() -> None:
    """parties is split into party1/party2 on the partial; everything else must mirror."""
    expected = (set(NdaFormValues.model_fields.keys()) - {"parties"}) | {"party1", "party2"}
    assert set(PartialNdaFormValues.model_fields.keys()) == expected
