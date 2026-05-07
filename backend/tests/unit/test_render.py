from pathlib import Path

import pytest

from prelegal.models import NdaFormValues
from prelegal.render import escape_html, render_nda

TEMPLATES_DIR = Path(__file__).resolve().parents[2].parent / "templates"


def make_values(**overrides) -> NdaFormValues:
    base = {
        "title": "ACME × Globex Mutual NDA",
        "purpose": "Evaluate a potential commercial relationship.",
        "effectiveDate": "2026-05-06",
        "mndaTerm": {"type": "expires", "years": 2},
        "termOfConfidentiality": {"type": "years", "years": 3},
        "governingLaw": "Delaware",
        "jurisdiction": "New Castle County, Delaware",
        "modifications": "",
        "parties": [
            {
                "printName": "Alice Example",
                "title": "CEO",
                "company": "ACME Inc.",
                "noticeAddress": "1 ACME Way, Springfield",
                "signedDate": "",
            },
            {
                "printName": "Bob Sample",
                "title": "CTO",
                "company": "Globex LLC",
                "noticeAddress": "2 Globex Ave, Springfield",
                "signedDate": "2026-05-07",
            },
        ],
    }
    base.update(overrides)
    return NdaFormValues.model_validate(base)


def test_escape_html_replaces_dangerous_characters():
    assert escape_html('<script>alert("x")</script>') == (
        "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"
    )
    assert escape_html("Tom & Jerry's") == "Tom &amp; Jerry&#39;s"


def test_render_includes_cover_and_standard_terms():
    md = render_nda(make_values(), TEMPLATES_DIR)
    assert md.startswith("# Mutual Non-Disclosure Agreement")
    assert "## Cover Page" in md
    assert "\n---\n" in md
    assert "**Party 1**" in md and "**Party 2**" in md
    assert "ACME Inc." in md and "Globex LLC" in md


def test_expires_term_renders_year_count_and_correct_checkbox():
    md = render_nda(make_values(mndaTerm={"type": "expires", "years": 5}), TEMPLATES_DIR)
    assert "- [x] Expires 5 year(s) from Effective Date." in md
    assert "- [ ] Continues until terminated" in md


def test_continues_term_uses_placeholder_year_count():
    md = render_nda(make_values(mndaTerm={"type": "continues"}), TEMPLATES_DIR)
    assert "- [ ] Expires [N] year(s) from Effective Date." in md
    assert "- [x] Continues until terminated" in md


def test_perpetuity_confidentiality_renders_placeholder_years_and_checkbox():
    md = render_nda(
        make_values(termOfConfidentiality={"type": "perpetuity"}), TEMPLATES_DIR
    )
    assert "- [ ] [N] year(s) from Effective Date" in md
    assert "- [x] In perpetuity." in md


def test_template_placeholders_are_replaced_with_bold_values():
    md = render_nda(make_values(), TEMPLATES_DIR)
    assert '<span class="coverpage_link">' not in md
    assert "**Evaluate a potential commercial relationship.**" in md
    assert "**Delaware**" in md
    assert "**New Castle County, Delaware**" in md


def test_user_supplied_html_is_escaped():
    md = render_nda(
        make_values(purpose='<img src=x onerror="alert(1)">'),
        TEMPLATES_DIR,
    )
    assert "<img" not in md
    assert "&lt;img" in md


def test_modifications_renders_none_label_when_blank():
    md = render_nda(make_values(modifications="   "), TEMPLATES_DIR)
    assert "_None._" in md


def test_modifications_text_appears_when_provided():
    md = render_nda(make_values(modifications="Section 4 deleted."), TEMPLATES_DIR)
    assert "Section 4 deleted." in md
    assert "_None._" not in md


def test_unsigned_party_uses_underline_placeholder():
    md = render_nda(make_values(), TEMPLATES_DIR)
    assert "- **Signed Date**: _______________" in md
    assert "- **Signed Date**: 2026-05-07" in md


def test_invalid_year_count_rejected_by_model():
    with pytest.raises(Exception):
        make_values(mndaTerm={"type": "expires", "years": 99})


def test_invalid_calendar_date_rejected_by_model():
    """`2026-02-30` matches the regex but isn't a real date."""
    with pytest.raises(Exception):
        make_values(effectiveDate="2026-02-30")
    with pytest.raises(Exception):
        make_values(effectiveDate="2026-13-01")
