"""Tests for the LLM helper. The completion() call is not exercised here —
integration tests cover wiring via monkeypatch, and the real model is
exercised manually."""

from __future__ import annotations

import json

from prelegal.llm import build_system_prompt
from prelegal.models import PartialNdaFormValues, PartialParty


def test_system_prompt_lists_required_fields() -> None:
    prompt = build_system_prompt(PartialNdaFormValues())
    for field in (
        "title",
        "effectiveDate",
        "mndaTerm",
        "termOfConfidentiality",
        "governingLaw",
        "jurisdiction",
        "party1",
        "party2",
    ):
        assert field in prompt


def test_system_prompt_embeds_current_values_as_alias_json() -> None:
    values = PartialNdaFormValues(
        title="Draft",
        governing_law="Delaware",
        party1=PartialParty(company="ACME"),
    )
    prompt = build_system_prompt(values)
    # Find the JSON blob embedded after the marker.
    marker = "Current known values (JSON): "
    start = prompt.index(marker) + len(marker)
    state_json = prompt[start:].splitlines()[0]
    state = json.loads(state_json)
    assert state == {
        "title": "Draft",
        "governingLaw": "Delaware",
        "party1": {"company": "ACME"},
    }


def test_system_prompt_omits_unset_fields() -> None:
    prompt = build_system_prompt(PartialNdaFormValues())
    marker = "Current known values (JSON): "
    start = prompt.index(marker) + len(marker)
    state_json = prompt[start:].splitlines()[0]
    assert json.loads(state_json) == {}
