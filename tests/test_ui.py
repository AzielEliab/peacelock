"""Local UI page exposes open/seal/break/verify and honest scope."""

from __future__ import annotations

from peacelock.ui import PAGE, render_page, wants_json


def test_ui_has_ops() -> None:
    for token in ("btn-open", "btn-seal", "btn-break", "btn-verify", "btn-upload", "btn-health", "btn-skill"):
        assert token in PAGE
    assert "btn-doctor" not in PAGE
    assert "HARD_DUTY" in PAGE
    assert "ABSENT" in PAGE or "transcript" in PAGE.lower()
    assert "Aziel Eliab" in PAGE
    assert "prefers-color-scheme" in PAGE
    assert ":focus-visible" in PAGE
    assert "Open quiet window" in PAGE
    assert ">Advanced<" in PAGE


def test_honest_scope_stays_under_about() -> None:
    html = render_page()
    assert html.find("Open quiet window") < html.find("THIS IS NOT")
    assert html.find("<summary>About</summary>") < html.find("THIS IS NOT")


def test_accept_json_prefers_machines() -> None:
    assert wants_json("application/json")
    assert wants_json("application/json, text/html;q=0.8")
    assert not wants_json("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    assert not wants_json(None)
