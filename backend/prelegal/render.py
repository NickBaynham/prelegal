"""Render an NDA cover page and standard terms from form values.

Port of frontend/lib/render.ts. Output is markdown intended for both
react-markdown rendering and downstream HTML conversion via marked, so all
user-supplied strings are HTML-escaped.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from .models import NdaFormValues, Party  # noqa: F401  (Party re-exported for tests)

_ESCAPE_MAP = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}
_ESCAPE_RE = re.compile("[&<>\"']")


def escape_html(text: str) -> str:
    return _ESCAPE_RE.sub(lambda m: _ESCAPE_MAP[m.group(0)], text)


def _describe_mnda_term(term: NdaFormValues) -> str:
    t = term.mnda_term
    if t.type == "expires":
        return f"{t.years} year(s) from the Effective Date"
    return "Continues until terminated in accordance with the terms of this MNDA"


def _describe_term_of_confidentiality(values: NdaFormValues) -> str:
    t = values.term_of_confidentiality
    if t.type == "years":
        return (
            f"{t.years} year(s) from the Effective Date "
            "(and, for trade secrets, until the information is no longer "
            "a trade secret under applicable law)"
        )
    return "In perpetuity"


def _checkbox(selected: bool) -> str:
    return "- [x]" if selected else "- [ ]"


def _render_party(party: Party, label: str) -> str:
    signed = party.signed_date or "_______________"
    lines = [
        f"**{escape_html(label)}**",
        "",
        f"- **Print Name**: {escape_html(party.print_name)}",
        f"- **Title**: {escape_html(party.title)}",
        f"- **Company**: {escape_html(party.company)}",
        f"- **Notice Address**: {escape_html(party.notice_address)}",
        f"- **Signed Date**: {escape_html(signed)}",
        "- **Signature**: _______________________________",
    ]
    return "\n".join(lines)


def _render_cover_page(values: NdaFormValues) -> str:
    party1, party2 = values.parties
    mnda_expires_label = (
        f"{values.mnda_term.years} year(s)"
        if values.mnda_term.type == "expires"
        else "[N] year(s)"
    )
    confidentiality_years_label = (
        f"{values.term_of_confidentiality.years} year(s)"
        if values.term_of_confidentiality.type == "years"
        else "[N] year(s)"
    )
    modifications = (
        escape_html(values.modifications) if values.modifications.strip() else "_None._"
    )
    lines = [
        "# Mutual Non-Disclosure Agreement",
        "",
        "## Cover Page",
        "",
        "This Mutual Non-Disclosure Agreement (the “MNDA”) consists of "
        "(1) this Cover Page and (2) the Common Paper Mutual NDA Standard Terms "
        "Version 1.0 reproduced below. Any modifications to the Standard Terms "
        "appear under “MNDA Modifications” on this Cover Page and control "
        "over conflicts with the Standard Terms.",
        "",
        "### Purpose",
        escape_html(values.purpose),
        "",
        "### Effective Date",
        escape_html(values.effective_date),
        "",
        "### MNDA Term",
        f"{_checkbox(values.mnda_term.type == 'expires')} Expires {mnda_expires_label} "
        "from Effective Date.",
        f"{_checkbox(values.mnda_term.type == 'continues')} Continues until terminated "
        "in accordance with the terms of the MNDA.",
        "",
        "### Term of Confidentiality",
        f"{_checkbox(values.term_of_confidentiality.type == 'years')} "
        f"{confidentiality_years_label} from Effective Date, but in the case of "
        "trade secrets until Confidential Information is no longer considered a "
        "trade secret under applicable laws.",
        f"{_checkbox(values.term_of_confidentiality.type == 'perpetuity')} In perpetuity.",
        "",
        "### Governing Law & Jurisdiction",
        f"Governing Law: {escape_html(values.governing_law)}",
        "",
        f"Jurisdiction: {escape_html(values.jurisdiction)}",
        "",
        "### MNDA Modifications",
        modifications,
        "",
        "### Signatures",
        "By signing this Cover Page, each party agrees to enter into this MNDA "
        "as of the Effective Date.",
        "",
        _render_party(party1, "Party 1"),
        "",
        _render_party(party2, "Party 2"),
        "",
    ]
    return "\n".join(lines)


@lru_cache(maxsize=8)
def _load_template(path: str) -> str:
    return Path(path).read_text(encoding="utf8")


def _fill_standard_terms(values: NdaFormValues, template_path: Path) -> str:
    body = _load_template(str(template_path))
    replacements: dict[str, str] = {
        "Purpose": escape_html(values.purpose),
        "Effective Date": escape_html(values.effective_date),
        "MNDA Term": _describe_mnda_term(values),
        "Term of Confidentiality": _describe_term_of_confidentiality(values),
        "Governing Law": escape_html(values.governing_law),
        "Jurisdiction": escape_html(values.jurisdiction),
    }
    for field_name, value in replacements.items():
        body = body.replace(
            f'<span class="coverpage_link">{field_name}</span>',
            f"**{value}**",
        )
    return body


def render_nda(values: NdaFormValues, templates_dir: Path) -> str:
    template_path = templates_dir / "Mutual-NDA.md"
    cover = _render_cover_page(values)
    terms = _fill_standard_terms(values, template_path)
    return f"{cover}\n\n---\n\n{terms}\n"
