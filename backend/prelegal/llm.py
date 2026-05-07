"""LiteLLM/OpenRouter chat client, pinned to Cerebras per the project skill."""

from __future__ import annotations

from litellm import completion

from .models import ChatMessage, ChatResponse, PartialNdaFormValues

_MODEL = "openrouter/openai/gpt-oss-120b"
_EXTRA_BODY = {"provider": {"order": ["cerebras"]}}

_SYSTEM_PROMPT_PREFIX = """You are an assistant helping users draft a Common Paper
Mutual Non-Disclosure Agreement (Mutual NDA).

Your job is to:
1. Answer questions about NDA fields clearly and concisely.
2. Extract field values from what the user tells you, returning them in `extractedValues`.
3. Politely ask for any missing required fields, one at a time.

Required fields:
- title: short name for the agreement.
- purpose: how confidential information may be used.
- effectiveDate: ISO date YYYY-MM-DD.
- mndaTerm: either {"type": "expires", "years": N} (1-50) or {"type": "continues"}.
- termOfConfidentiality: either {"type": "years", "years": N} (1-99) or {"type": "perpetuity"}.
- governingLaw: a US state (e.g. "Delaware").
- jurisdiction: city/county and state (e.g. "New Castle County, Delaware").
- modifications: optional free text; may be empty.
- party1 and party2: each requires printName, title, company, noticeAddress.
  signedDate is optional.

Rules:
- Only return fields in `extractedValues` you are confident about. Set unknowns to null.
- For mndaTerm and termOfConfidentiality, return the FULL discriminated-union object
  or null — never partially-formed.
- Keep `assistantMessage` short and friendly (1-3 sentences).
- Do not invent values. If the user is ambiguous, ask a clarifying question.
- Stay focused on this Mutual NDA — politely redirect off-topic requests.
"""


def build_system_prompt(current_values: PartialNdaFormValues) -> str:
    """Return the system prompt for one chat turn, including current partial state."""
    state = current_values.model_dump_json(by_alias=True, exclude_none=True)
    return f"{_SYSTEM_PROMPT_PREFIX}\nCurrent known values (JSON): {state}\n"


def chat_assist(
    messages: list[ChatMessage],
    current_values: PartialNdaFormValues,
    api_key: str,
) -> ChatResponse:
    payload = [{"role": "system", "content": build_system_prompt(current_values)}]
    payload.extend({"role": m.role, "content": m.content} for m in messages)

    response = completion(
        model=_MODEL,
        messages=payload,
        response_format=ChatResponse,
        structured_output=True,
        reasoning_effort="low",
        extra_body=_EXTRA_BODY,
        api_key=api_key,
    )
    raw = response.choices[0].message.content
    return ChatResponse.model_validate_json(raw)
